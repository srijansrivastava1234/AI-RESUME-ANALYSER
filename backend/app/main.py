import os
# Force pure-python protobuf implementation to support Python 3.14+ pre-releases
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import logging
import time
from typing import Optional, List

APP_VERSION = "1.6.0"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_COMPARE_FILES = 5

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from app.analyzer import analyze_resume
from app.rewriter import optimize_bullet_point
from app.comparator import compare_resumes
from app.hygiene import audit_resume_hygiene
from app.xyz_scorer import score_resume_bullet, evaluate_bullet_verb_diversity
from app.compliance import audit_ats_compliance
from app.agent_prompt import generate_agent_refactor_prompt, generate_byok_export_package
from app.logging_config import setup_logging, generate_request_id
from dotenv import load_dotenv

# Load environmental variables from .env if present
load_dotenv()

# Initialize structured JSON logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("ResumeAnalyserAPI")

# Initialize rate limiter (IP-based, 10 requests/minute for analysis endpoints)
limiter = Limiter(key_func=get_remote_address)

class OptimizeBulletRequest(BaseModel):
    bullet: str = Field(..., min_length=5, description="The resume bullet point text to optimize")
    target_role: Optional[str] = Field(None, description="Optional target job title or role context")

class ScoreBulletRequest(BaseModel):
    bullet: str = Field(..., min_length=1, description="The resume bullet point text to evaluate")
    seniority: Optional[str] = Field("mid", description="Seniority level: 'junior', 'mid', 'senior', or 'staff'")

class ComplianceAuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="The plain text of the resume to audit")
    job_description: Optional[str] = Field(None, description="Optional target job description")
    seniority: Optional[str] = Field("mid", description="Seniority level: 'junior', 'mid', 'senior', 'staff', or 'executive'")
    target_pages: Optional[int] = Field(1, description="Expected page budget: 1 or 2 pages")

class AgentPromptRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="The plain text of the resume")
    job_description: Optional[str] = Field(None, description="Optional target job description")
    seniority: Optional[str] = Field("mid", description="Target seniority level")
    missing_keywords: Optional[List[str]] = Field(None, description="Optional identified missing keywords")
    weak_bullets: Optional[List[str]] = Field(None, description="Optional weak bullets to rewrite")

class VerbDiversityRequest(BaseModel):
    bullets: List[str] = Field(..., min_length=1, description="List of resume bullet points to evaluate for verb diversity")

app = FastAPI(
    title="AI Resume Analyser API",
    description="High-performance asynchronous API for resume parsing, ATS scoring, and generative AI feedback using Google Gemini.",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Attach rate limiter state to the app
app.state.limiter = limiter

# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. You are rate-limited to 10 analysis requests per minute. Please wait before retrying.",
            "retry_after_seconds": 60
        }
    )

# Custom performance, security, and request tracing headers middleware
@app.middleware("http")
async def add_process_time_and_security_headers(request: Request, call_next):
    request_id = generate_request_id()
    start_time = time.time()

    # Attach request_id to request state for downstream access
    request.state.request_id = request_id

    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Client: {get_remote_address(request)}"
    )

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    logger.info(
        f"[{request_id}] Response {response.status_code} in {process_time:.4f}s"
    )

    return response

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
            "/api/analyze": "POST - Upload PDF/DOCX/TXT resume and optional job description to get ATS analysis",
            "/api/compare": "POST - Upload multiple resumes for side-by-side ATS ranking",
            "/api/hygiene": "POST - Evaluate ATS formatting hygiene, contact completeness, and section headers",
            "/api/score-bullet": "POST - Deterministic Google/IBM XYZ mathematical bullet impact evaluation",
            "/api/optimize-bullet": "POST - Optimize single resume bullet point into XYZ format",
            "/api/compliance-audit": "POST - Deterministic 4-Pillar ATS Compliance Audit & Regulatory Safe Harbor check",
            "/api/agent-prompt": "POST - Synthesize Agent-Native BYOK refactoring prompt for external LLMs",
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
@limiter.limit("10/minute")
async def analyze_resume_endpoint(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(None)
):
    request_id = getattr(request.state, "request_id", "unknown")
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
        logger.info(f"[{request_id}] Received file: {file.filename} for analysis")
        
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
        logger.info(f"[{request_id}] Extracted {len(extracted_text)} characters of text in {parse_duration:.3f}s")
        
        # 2. Analyze using Gemini prompt engine
        analysis_start = time.time()
        analysis_report = analyze_resume(extracted_text, job_description)
        analysis_duration = time.time() - analysis_start
        
        # 3. Augment with deterministic 4-Pillar Compliance Scorecard & BYOK Agent Prompt
        compliance_audit = audit_ats_compliance(extracted_text, job_description)
        byok_prompt = generate_agent_refactor_prompt(
            resume_text=extracted_text,
            job_description=job_description,
            target_seniority="mid",
            missing_keywords=compliance_audit.get("pillars", {}).get("keywords", {}).get("missing_keywords", [])
        )
        analysis_report["compliance_audit"] = compliance_audit
        analysis_report["byok_agent_prompt"] = byok_prompt
        
        total_duration = time.time() - start_time
        logger.info(f"[{request_id}] Analysis completed in {analysis_duration:.3f}s. Total time: {total_duration:.3f}s")
        
        return {
            "filename": file.filename,
            "char_count": len(extracted_text),
            "page_count": page_count,
            "extracted_text": extracted_text,
            "report": analysis_report
        }
        
    except ValueError as val_err:
        logger.warning(f"[{request_id}] Validation issue: {str(val_err)}")
        raise HTTPException(status_code=400, detail=str(val_err))
        
    except Exception as e:
        logger.error(f"[{request_id}] Error during resume analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )

@app.post("/api/compare")
@limiter.limit("5/minute")
async def compare_resumes_endpoint(
    request: Request,
    files: List[UploadFile] = File(...),
    job_description: str = Form(None)
):
    """
    Accepts multiple resume files and a shared job description, analyzes each,
    and returns a ranked comparison report sorted by ATS score.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 resume files are required for comparison."
        )
    if len(files) > MAX_COMPARE_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_COMPARE_FILES} files can be compared at once."
        )

    # Validate all file extensions first
    for file in files:
        filename_lower = file.filename.lower()
        if not (filename_lower.endswith(".pdf") or filename_lower.endswith(".docx") or filename_lower.endswith(".txt")):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format for '{file.filename}'. Only PDF, DOCX, and TXT files are supported."
            )

    try:
        start_time = time.time()
        logger.info(f"[{request_id}] Comparing {len(files)} resumes")

        resume_texts = []
        for file in files:
            filename_lower = file.filename.lower()
            file_bytes = await file.read()
            if filename_lower.endswith(".pdf"):
                text, _ = extract_text_from_pdf(file_bytes)
            elif filename_lower.endswith(".docx"):
                text = extract_text_from_docx(file_bytes)
            else:
                text = extract_text_from_txt(file_bytes)

            resume_texts.append({"filename": file.filename, "text": text})

        comparison_report = compare_resumes(resume_texts, job_description)

        total_duration = time.time() - start_time
        logger.info(f"[{request_id}] Comparison completed in {total_duration:.3f}s")

        return comparison_report

    except ValueError as val_err:
        logger.warning(f"[{request_id}] Comparison validation: {str(val_err)}")
        raise HTTPException(status_code=400, detail=str(val_err))

    except Exception as e:
        logger.error(f"[{request_id}] Error during comparison: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during resume comparison: {str(e)}"
        )

@app.post("/api/hygiene")
@limiter.limit("20/minute")
async def check_hygiene_endpoint(
    request: Request,
    file: UploadFile = File(...),
):
    """
    Evaluates resume formatting hygiene, section completeness, and contact details
    without requiring LLM inference.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".pdf") or filename_lower.endswith(".docx") or filename_lower.endswith(".txt")):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format for '{file.filename}'. Only PDF, DOCX, and TXT files are supported."
        )

    try:
        file_bytes = await file.read()
        if filename_lower.endswith(".pdf"):
            text, _ = extract_text_from_pdf(file_bytes)
        elif filename_lower.endswith(".docx"):
            text = extract_text_from_docx(file_bytes)
        else:
            text = extract_text_from_txt(file_bytes)

        hygiene_report = audit_resume_hygiene(text)
        return {
            "filename": file.filename,
            "hygiene": hygiene_report
        }
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"[{request_id}] Error in hygiene endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit hygiene: {str(err)}")

@app.post("/api/score-bullet")
@limiter.limit("20/minute")
def score_bullet_endpoint(request: Request, payload: ScoreBulletRequest):
    """
    Evaluates a resume bullet point using the deterministic Google/IBM X-Y-Z formula:
    'Accomplished [X] as measured by [Y], by doing [Z]'
    """
    try:
        seniority = payload.seniority.lower() if payload.seniority else "mid"
        if seniority not in ["junior", "mid", "senior", "staff"]:
            seniority = "mid"
        result = score_resume_bullet(payload.bullet, seniority=seniority)
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"Error in bullet scoring: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to score bullet: {str(err)}")

@app.post("/api/optimize-bullet")
@limiter.limit("20/minute")
def optimize_bullet_endpoint(request: Request, payload: OptimizeBulletRequest):
    """
    Transforms a single resume bullet point into a high-impact, quantifiable statement
    following Google's XYZ formula.
    """
    try:
        result = optimize_bullet_point(payload.bullet, payload.target_role)
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"Error in bullet optimization: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize bullet: {str(err)}")

@app.post("/api/compliance-audit")
@limiter.limit("20/minute")
def audit_compliance_endpoint(request: Request, payload: ComplianceAuditRequest):
    """
    Executes deterministic 4-Pillar ATS Compliance Audit & Regulatory Safe Harbor check.
    """
    try:
        result = audit_ats_compliance(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            target_seniority=payload.seniority or "mid",
            target_pages=payload.target_pages or 1
        )
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"Error in compliance audit endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit ATS compliance: {str(err)}")

@app.post("/api/agent-prompt")
@limiter.limit("30/minute")
def generate_agent_prompt_endpoint(request: Request, payload: AgentPromptRequest):
    """
    Synthesizes an Agent-Native BYOK refactoring prompt formatted for external frontier LLMs.
    """
    try:
        prompt = generate_agent_refactor_prompt(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            target_seniority=payload.seniority or "mid",
            missing_keywords=payload.missing_keywords,
            identified_weak_bullets=payload.weak_bullets
        )
        return {
            "seniority": payload.seniority or "mid",
            "agent_prompt": prompt
        }
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"Error in agent prompt endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to generate agent prompt: {str(err)}")

@app.post("/api/verb-diversity")
@limiter.limit("30/minute")
def evaluate_verb_diversity_endpoint(request: Request, payload: VerbDiversityRequest):
    """
    Evaluates action verb distribution, redundancy, and diversity score across candidate bullet points.
    """
    try:
        result = evaluate_bullet_verb_diversity(payload.bullets)
        return result
    except Exception as err:
        logger.error(f"Error in verb diversity endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate verb diversity: {str(err)}")


