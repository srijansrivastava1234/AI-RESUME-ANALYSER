import os
# Force pure-python protobuf implementation to support Python 3.14+ pre-releases
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.parser import extract_text_from_pdf
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
    # Verify file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF files are supported."
        )
        
    try:
        logger.info(f"Received file: {file.filename} for analysis")
        
        # Read file bytes
        file_bytes = await file.read()
        
        # 1. Parse text from PDF
        extracted_text = extract_text_from_pdf(file_bytes)
        logger.info(f"Extracted {len(extracted_text)} characters of text from PDF")
        
        # 2. Analyze using Gemini prompt engine
        analysis_report = analyze_resume(extracted_text, job_description)
        logger.info("Resume analysis completed successfully")
        
        return {
            "filename": file.filename,
            "char_count": len(extracted_text),
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
