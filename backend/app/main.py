import os
# Force pure-python protobuf implementation to support Python 3.14+ pre-releases
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import logging
import time

APP_VERSION = "1.1.0"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
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
        "version": APP_VERSION,
        "service": "AI Resume Analyser Service",
        "endpoints": {
            "/api/analyze": "POST - Upload PDF resume and optional job description to get ATS analysis",
            "/api/health": "GET - Service health check"
        }
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint for uptime monitoring and deployment readiness."""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "service": "AI Resume Analyser API",
        "supported_formats": ["pdf", "docx", "txt"],
        "max_file_size_mb": MAX_FILE_SIZE_BYTES // (1024 * 1024)
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
        # Enforce file size limit early to avoid loading large files into memory
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB. Received {file_size // (1024*1024)}MB."
            )
        start_time = time.time()
        logger.info(f"Received file: {file.filename} for analysis")
        
        # Read file bytes
        file_bytes = await file.read()
        
        # 1. Parse text based on format
        parse_start = time.time()
        page_count = None
        if filename_lower.endswith(".pdf"):
            extracted_text, page_count = extract_text_from_pdf(file_bytes)
        elif filename_lower.endswith(".docx"):
            extracted_text = extract_text_from_docx(file_bytes)
        else:
            extracted_text = extract_text_from_txt(file_bytes)
            
        parse_duration = time.time() - parse_start
        logger.info(f"Extracted {len(extracted_text)} characters of text in {parse_duration:.3f}s")
        
        # 2. Analyze using Gemini prompt engine
        analysis_start = time.time()
        analysis_report = analyze_resume(extracted_text, job_description)
        analysis_duration = time.time() - analysis_start
        
        total_duration = time.time() - start_time
        logger.info(f"Analysis completed in {analysis_duration:.3f}s. Total time: {total_duration:.3f}s")
        
        return {
            "filename": file.filename,
            "char_count": len(extracted_text),
            "page_count": page_count,
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
