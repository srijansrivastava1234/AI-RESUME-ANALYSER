import os
# Force pure-python protobuf implementation to support Python 3.14+ pre-releases
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from app.analyzer import analyze_resume
from dotenv import load_dotenv

# Load environmental variables from .env if present
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResumeAnalyserAPI")

app = FastAPI(title="AI Resume Analyser Backend")

# Enable CORS for frontend dashboard connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "service": "AI Resume Analyser Service",
        "endpoints": {
            "/api/analyze": "POST - Upload PDF resume and optional job description to get ATS analysis"
        }
    }

@app.post("/api/analyze")
async def analyze_resume_endpoint(
    file: UploadFile = File(...),
    job_description: str = Form(None)
):
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".pdf") or filename_lower.endswith(".docx") or filename_lower.endswith(".txt")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF, DOCX, and TXT files are supported."
        )
        
    try:
        logger.info(f"Received file: {file.filename} for analysis")
        
        # Read file bytes
        file_bytes = await file.read()
        
        # 1. Parse text based on format
        if filename_lower.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_bytes)
        elif filename_lower.endswith(".docx"):
            extracted_text = extract_text_from_docx(file_bytes)
        else:
            extracted_text = extract_text_from_txt(file_bytes)
            
        logger.info(f"Extracted {len(extracted_text)} characters of text")
        
        # 2. Analyze using Gemini prompt engine
        analysis_report = analyze_resume(extracted_text, job_description)
        logger.info("Resume analysis completed successfully")
        
        return {
            "filename": file.filename,
            "char_count": len(extracted_text),
            "extracted_text": extracted_text,
            "report": analysis_report
        }
        
    except ValueError as val_err:
        logger.warning(f"Validation issue: {str(val_err)}")
        raise HTTPException(status_code=400, detail=str(val_err))
        
    except Exception as e:
        logger.error(f"Error during resume analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )
