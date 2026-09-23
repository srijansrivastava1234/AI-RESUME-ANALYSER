import os
# Force pure-python protobuf implementation to support Python 3.14+ pre-releases
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import logging
import time
from typing import Optional, List, Dict, Any

APP_VERSION = "2.4.0"
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
from app.viewport import audit_first_third_viewport
from app.acronyms import expand_technical_terms
from app.adverse_impact import audit_group_selection_rates
from app.hack_detector import detect_ats_hacks
from app.header_normalizer import audit_section_headers
from app.token_density import audit_token_density
from app.metric_validator import audit_bullet_metrics
from app.seniority_profiler import audit_seniority_distribution
from app.redaction import anonymize_resume_for_blind_audit
from app.layout_linearizer import simulate_recursive_xy_cut
from app.chronology import audit_career_chronology
from app.font_integrity import audit_font_cmap_integrity
from app.bm25_scorer import compute_bm25_plus
from app.contact_validator import audit_candidate_contact
from app.skill_classifier import audit_skills
from app.section_flow import audit_section_flow
from app.action_verb_analyzer import audit_action_verbs
from app.page_budget_analyzer import audit_page_budget
from app.readability import calculate_readability_metrics
from app.voice_detector import analyze_voice
from app.cliche_detector import audit_cliches
from app.metric_diversity import analyze_metric_diversity
from app.filename_auditor import audit_filename
from app.skill_recency import analyze_skill_recency
from app.bullet_length import analyze_bullet_lengths
from app.summary_classifier import classify_summary_style
from app.salary_detector import detect_salary_disclosures
from app.portfolio_validator import audit_portfolio_links
from app.pdf_layout import extract_pdf_layout_tokens
from app.jd_scraper import scrape_job_description
from app.ats_simulator import run_multi_ats_simulation
from app.interview_prep import generate_interview_prep
from app.resume_builder import parse_resume_to_structured_json, format_structured_resume_to_plain_text
from app.outreach import generate_outreach
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
    target_model: Optional[str] = Field("general", description="Target model architecture: 'claude', 'gpt', 'cursor', or 'general'")

class VerbDiversityRequest(BaseModel):
    bullets: List[str] = Field(..., min_length=1, description="List of resume bullet points to evaluate for verb diversity")

class ViewportAuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="The plain text of the resume to audit for viewport precision")
    target_skills: Optional[List[str]] = Field(None, description="Optional target skills to search in upper viewport")

class AcronymExpansionRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Text containing technical acronyms or terms to expand")

class AdverseImpactRequest(BaseModel):
    group_data: dict = Field(..., description="Dictionary mapping group names to {'total': int, 'selected': int}")

class DetectHacksRequest(BaseModel):
    text: str = Field(..., description="Resume plain text")
    raw_markup: Optional[str] = Field(None, description="Optional raw HTML/CSS/stream markup")

class AuditHeadersRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to audit section headers")

class TokenDensityRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Resume text to evaluate token density")
    language: Optional[str] = Field(None, description="Optional language override ('en', 'es', 'pt', 'fr', 'de')")

class ValidateMetricRequest(BaseModel):
    bullet: str = Field(..., min_length=1, description="Bullet statement to audit for quantifiable business metrics")

class SeniorityProfileRequest(BaseModel):
    bullets: List[str] = Field(..., description="List of resume achievement bullet points")
    target_tier: Optional[str] = Field("senior", description="Target seniority tier ('junior', 'mid', 'senior', 'staff', 'executive')")

class RedactPIIRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Resume text to anonymize for blind review")

class LayoutAuditRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The resume text to audit for layout linearization and XY-cut hazards")

class ChronologyAuditRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The resume text to audit for career chronology and employment gaps")

class FontIntegrityRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The resume text to audit for ISO 19005-2 PDF/A text layer and ligature health")

class BM25AuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="The resume text to evaluate using BM25+")
    target_keywords: List[str] = Field(..., description="List of target keywords or job competencies")

class ContactAuditRequest(BaseModel):
    email: Optional[str] = Field(None, description="Candidate email address")
    phone: Optional[str] = Field(None, description="Candidate phone number")
    links: Optional[List[str]] = Field(None, description="Candidate profile URLs (LinkedIn, GitHub, Portfolio)")
    text: Optional[str] = Field(None, description="Optional raw resume text for automatic contact extraction")

class SkillClassifyRequest(BaseModel):
    skills: List[str] = Field(..., description="List of candidate skills to classify")
    experience_text: Optional[str] = Field(None, description="Optional work experience text for substantiation cross-check")

class SectionFlowRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Resume text to evaluate section order and structural flow")
    is_early_career: Optional[bool] = Field(False, description="Whether to benchmark against early career / new grad profile")

class ActionVerbRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Resume text to evaluate action verb variety and fatigue")

class PageBudgetRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Resume text to evaluate page budget and spillover")
    target_pages: Optional[int] = Field(1, description="Target page budget (1 or 2)")

class ReadabilityRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to evaluate readability and grade levels")

class VoiceAuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to evaluate passive vs active voice")

class ClicheAuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to evaluate buzzwords and corporate clichés")

class MetricDiversityRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to evaluate metric breadth across dimensions")

class FilenameAuditRequest(BaseModel):
    filename: str = Field(..., min_length=1, description="Uploaded resume filename")
    candidate_name: Optional[str] = Field(None, description="Optional candidate full name")

class SkillRecencyRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to evaluate skill currency and tenure decay")
    current_year: Optional[int] = Field(2026, description="Current reference year")

class BulletLengthRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text containing bullet points to audit for length")

class SummaryStyleRequest(BaseModel):
    summary_text: str = Field(..., min_length=1, description="Resume summary or objective text to classify")

class SalaryAuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to audit for confidential salary disclosures")

class PortfolioLinksRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to audit for portfolio and profile URLs")

class ScrapeJobDescriptionRequest(BaseModel):
    url: str = Field(..., min_length=4, description="Target job description URL (e.g. Greenhouse, Lever, LinkedIn, etc.)")

class SimulateATSRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="The plain text of the resume to simulate across ATS engines")

class InterviewPrepRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Candidate resume text")
    job_description: Optional[str] = Field(None, description="Optional target job description")
    seniority: Optional[str] = Field("mid", description="Target seniority tier ('junior', 'mid', 'senior', 'staff', 'executive')")

class ParseStructuredResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Raw resume text to parse into structured JSON")

class FormatCleanTxtRequest(BaseModel):
    structured_resume: Dict[str, Any] = Field(..., description="Structured resume JSON object")

class GenerateOutreachRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Candidate resume text")
    job_description: Optional[str] = Field(None, description="Optional target job description")
    mode: Optional[str] = Field("cover_letter", description="Outreach mode ('cover_letter', 'linkedin_inmail', 'cold_email', 'follow_up')")
    tone: Optional[str] = Field("confident", description="Tone ('confident', 'direct', 'technical', 'executive')")
    recipient_name: Optional[str] = Field(None, description="Target recipient or recruiter name")
    company_name: Optional[str] = Field(None, description="Target company name")





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
        analysis_report["layout_linearization"] = simulate_recursive_xy_cut(extracted_text)
        analysis_report["career_chronology"] = audit_career_chronology(extracted_text)
        analysis_report["font_integrity"] = audit_font_cmap_integrity(extracted_text)
        
        # Ensure v2.2.0 diagnostics are attached
        if "bm25_audit" not in analysis_report:
            target_kws = (
                compliance_audit.get("pillars", {}).get("keywords", {}).get("detected_keywords", []) +
                compliance_audit.get("pillars", {}).get("keywords", {}).get("missing_keywords", [])
            )
            analysis_report["bm25_audit"] = compute_bm25_plus(extracted_text, target_kws)
        if "contact_audit" not in analysis_report:
            analysis_report["contact_audit"] = audit_candidate_contact(text=extracted_text)
        if "skill_classification" not in analysis_report:
            detected_skills = analysis_report.get("keywords", {}).get("detected", [])
            analysis_report["skill_classification"] = audit_skills(detected_skills, experience_text=extracted_text)

        
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
            identified_weak_bullets=payload.weak_bullets,
            target_model=payload.target_model or "general"
        )
        return {
            "seniority": payload.seniority or "mid",
            "target_model": payload.target_model or "general",
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

@app.post("/api/viewport-audit")
@limiter.limit("20/minute")
def audit_viewport_endpoint(request: Request, payload: ViewportAuditRequest):
    """
    Evaluates recruiter 6-second scan readability and accomplishment front-loading in upper 30% viewport.
    """
    try:
        result = audit_first_third_viewport(
            raw_text=payload.resume_text,
            target_skills=payload.target_skills
        )
        return result
    except Exception as err:
        logger.error(f"Error in viewport audit endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit viewport precision: {str(err)}")

@app.post("/api/expand-keywords")
@limiter.limit("30/minute")
def expand_keywords_endpoint(request: Request, payload: AcronymExpansionRequest):
    """
    Identifies technical abbreviations in text and resolves them to canonical industry terms.
    """
    try:
        result = expand_technical_terms(payload.text)
        return result
    except Exception as err:
        logger.error(f"Error in expand keywords endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to expand technical terms: {str(err)}")

@app.post("/api/adverse-impact")
@limiter.limit("15/minute")
def adverse_impact_endpoint(request: Request, payload: AdverseImpactRequest):
    """
    Audits selection rate parity and EEOC Four-Fifths compliance across candidate groups per NYC LL 144.
    """
    try:
        result = audit_group_selection_rates(payload.group_data)
        return result
    except Exception as err:
        logger.error(f"Error in adverse impact endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit adverse impact: {str(err)}")

@app.post("/api/detect-hacks")
@limiter.limit("30/minute")
def detect_hacks_endpoint(request: Request, payload: DetectHacksRequest):
    """
    Audits document for white-font stuffing, zero-opacity styles, micro-fonts, and invisible Unicode ink.
    """
    try:
        result = detect_ats_hacks(payload.text, raw_markup=payload.raw_markup)
        return result
    except Exception as err:
        logger.error(f"Error in detect hacks endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to detect ATS hacks: {str(err)}")

@app.post("/api/audit-headers")
@limiter.limit("30/minute")
def audit_headers_endpoint(request: Request, payload: AuditHeadersRequest):
    """
    Audits resume headings for Workday, Taleo, and enterprise ATS canonical schema compliance.
    """
    try:
        result = audit_section_headers(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit headers endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit section headers: {str(err)}")

@app.post("/api/token-density")
@limiter.limit("30/minute")
def token_density_endpoint(request: Request, payload: TokenDensityRequest):
    """
    Audits document for information signal-to-noise ratio, multi-lingual stopwords, and Type-Token Ratio.
    """
    try:
        result = audit_token_density(payload.text, force_lang=payload.language)
        return result
    except Exception as err:
        logger.error(f"Error in token density endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze token density: {str(err)}")

@app.post("/api/validate-metric")
@limiter.limit("30/minute")
def validate_metric_endpoint(request: Request, payload: ValidateMetricRequest):
    """
    Disambiguates bullet metrics into true business outcomes vs vanity counts and technical version false-positives.
    """
    try:
        result = audit_bullet_metrics(payload.bullet)
        return result
    except Exception as err:
        logger.error(f"Error in validate metric endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to validate metric: {str(err)}")

@app.post("/api/seniority-profile")
@limiter.limit("30/minute")
def seniority_profile_endpoint(request: Request, payload: SeniorityProfileRequest):
    """
    Audits resume accomplishment ratio against target seniority tier expectations (Junior to Executive).
    """
    try:
        result = audit_seniority_distribution(payload.bullets, target_tier=payload.target_tier or "senior")
        return result
    except Exception as err:
        logger.error(f"Error in seniority profile endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit seniority distribution: {str(err)}")

@app.post("/api/redact-pii")
@limiter.limit("30/minute")
def redact_pii_endpoint(request: Request, payload: RedactPIIRequest):
    """
    Sanitizes candidate resume by redacting PII, contact info, and age proxies for EEOC / NYC LL 144 blind review.
    """
    try:
        result = anonymize_resume_for_blind_audit(payload.text)
        return result
    except Exception as err:
        logger.error(f"Error in redact PII endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to redact candidate PII: {str(err)}")

@app.post("/api/audit-layout")
@limiter.limit("30/minute")
def audit_layout_endpoint(request: Request, payload: LayoutAuditRequest):
    """
    Simulates the Recursive XY-Cut algorithm and legacy ATS scanline sorting to audit multi-column risks.
    """
    try:
        result = simulate_recursive_xy_cut(payload.text)
        return result
    except Exception as err:
        logger.error(f"Error in audit layout endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit layout linearization: {str(err)}")

@app.post("/api/audit-chronology")
@limiter.limit("30/minute")
def audit_chronology_endpoint(request: Request, payload: ChronologyAuditRequest):
    """
    Audits resume career timeline, standardizes date ranges, detects employment gaps, and counts YoE.
    """
    try:
        result = audit_career_chronology(payload.text)
        return result
    except Exception as err:
        logger.error(f"Error in audit chronology endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit career chronology: {str(err)}")

@app.post("/api/audit-font-integrity")
@limiter.limit("30/minute")
def audit_font_integrity_endpoint(request: Request, payload: FontIntegrityRequest):
    """
    Audits document for ISO 19005-2 PDF/A text layer compliance, PUA glyphs, and decomposes typographic ligatures.
    """
    try:
        result = audit_font_cmap_integrity(payload.text)
        return result
    except Exception as err:
        logger.error(f"Error in audit font integrity endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit font integrity: {str(err)}")

@app.post("/api/audit-bm25")
@limiter.limit("30/minute")
def audit_bm25_endpoint(request: Request, payload: BM25AuditRequest):
    """
    Computes Okapi BM25+ relevance score with term frequency saturation and length normalization.
    """
    try:
        result = compute_bm25_plus(payload.resume_text, payload.target_keywords)
        return result
    except Exception as err:
        logger.error(f"Error in audit BM25 endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit BM25+ relevance: {str(err)}")

@app.post("/api/audit-contact")
@limiter.limit("30/minute")
def audit_contact_endpoint(request: Request, payload: ContactAuditRequest):
    """
    Audits candidate contact coordinates against RFC 5322, ITU-T E.164, and HTTPS link security.
    """
    try:
        result = audit_candidate_contact(
            email=payload.email,
            phone=payload.phone,
            links=payload.links,
            text=payload.text
        )
        return result
    except Exception as err:
        logger.error(f"Error in audit contact endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit candidate contact: {str(err)}")

@app.post("/api/classify-skills")
@limiter.limit("30/minute")
def classify_skills_endpoint(request: Request, payload: SkillClassifyRequest):
    """
    Classifies skills into hard vs soft competencies, detects buzzword dilution, and checks experience substantiation.
    """
    try:
        result = audit_skills(payload.skills, experience_text=payload.experience_text)
        return result
    except Exception as err:
        logger.error(f"Error in classify skills endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to classify candidate skills: {str(err)}")

@app.post("/api/audit-section-flow")
@limiter.limit("30/minute")
def audit_section_flow_endpoint(request: Request, payload: SectionFlowRequest):
    """
    Audits resume section sequence, identifying jarring inversions, misplaced sections, or buried qualifications.
    """
    try:
        result = audit_section_flow(payload.resume_text, is_early_career=payload.is_early_career)
        return result
    except Exception as err:
        logger.error(f"Error in audit section flow endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit section flow: {str(err)}")

@app.post("/api/audit-action-verbs")
@limiter.limit("30/minute")
def audit_action_verbs_endpoint(request: Request, payload: ActionVerbRequest):
    """
    Audits resume bullet action verbs for variety, tier distribution, and repetitive fatigue.
    """
    try:
        result = audit_action_verbs(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit action verbs endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit action verbs: {str(err)}")

@app.post("/api/audit-page-budget")
@limiter.limit("30/minute")
def audit_page_budget_endpoint(request: Request, payload: PageBudgetRequest):
    """
    Audits page budget adherence and flags dangerous trailing spillover.
    """
    try:
        result = audit_page_budget(payload.resume_text, target_pages=payload.target_pages or 1)
        return result
    except Exception as err:
        logger.error(f"Error in audit page budget endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit page budget: {str(err)}")

@app.post("/api/audit-readability")
@limiter.limit("30/minute")
def audit_readability_endpoint(request: Request, payload: ReadabilityRequest):
    """
    Audits resume text for Flesch Reading Ease, Flesch-Kincaid Grade Level, and Gunning Fog Index.
    """
    try:
        result = calculate_readability_metrics(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit readability endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate readability metrics: {str(err)}")

@app.post("/api/audit-voice")
@limiter.limit("30/minute")
def audit_voice_endpoint(request: Request, payload: VoiceAuditRequest):
    """
    Audits resume bullet points and sentences for passive voice density and active voice ratio.
    """
    try:
        result = analyze_voice(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit voice endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate voice: {str(err)}")

@app.post("/api/audit-cliches")
@limiter.limit("30/minute")
def audit_cliches_endpoint(request: Request, payload: ClicheAuditRequest):
    """
    Audits resume text for weak corporate clichés, buzzwords, and vague fluff.
    """
    try:
        result = audit_cliches(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit cliches endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit clichés: {str(err)}")

@app.post("/api/audit-metric-diversity")
@limiter.limit("30/minute")
def audit_metric_diversity_endpoint(request: Request, payload: MetricDiversityRequest):
    """
    Classifies quantified bullet points into financial, percentage, scale, velocity, and leadership dimensions.
    """
    try:
        result = analyze_metric_diversity(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit metric diversity endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate metric diversity: {str(err)}")

@app.post("/api/audit-filename")
@limiter.limit("30/minute")
def audit_filename_endpoint(request: Request, payload: FilenameAuditRequest):
    """
    Audits resume filename against enterprise ATS ingestion naming standards.
    """
    try:
        result = audit_filename(payload.filename, candidate_name=payload.candidate_name or "")
        return result
    except Exception as err:
        logger.error(f"Error in audit filename endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit filename: {str(err)}")

@app.post("/api/audit-skill-recency")
@limiter.limit("30/minute")
def audit_skill_recency_endpoint(request: Request, payload: SkillRecencyRequest):
    """
    Audits skill recency across career timeline, detecting active modern tools vs dormant legacy stacks.
    """
    try:
        result = analyze_skill_recency(payload.resume_text, current_year=payload.current_year or 2026)
        return result
    except Exception as err:
        logger.error(f"Error in audit skill recency endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit skill recency: {str(err)}")

@app.post("/api/audit-bullet-lengths")
@limiter.limit("30/minute")
def audit_bullet_lengths_endpoint(request: Request, payload: BulletLengthRequest):
    """
    Audits individual bullet points against the 15-25 words sweet-spot and flags stubs/run-ons.
    """
    try:
        result = analyze_bullet_lengths(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit bullet lengths endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit bullet lengths: {str(err)}")

@app.post("/api/audit-summary-style")
@limiter.limit("30/minute")
def audit_summary_style_endpoint(request: Request, payload: SummaryStyleRequest):
    """
    Classifies resume summary into modern Executive Value Proposition vs outdated Objective Statement.
    """
    try:
        result = classify_summary_style(payload.summary_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit summary style endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to classify summary style: {str(err)}")

@app.post("/api/audit-salary-disclosures")
@limiter.limit("30/minute")
def audit_salary_disclosures_endpoint(request: Request, payload: SalaryAuditRequest):
    """
    Scans resume text for inadvertent confidential personal compensation or CTC disclosures.
    """
    try:
        result = detect_salary_disclosures(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit salary disclosures endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit salary disclosures: {str(err)}")

@app.post("/api/audit-portfolio-links")
@limiter.limit("30/minute")
def audit_portfolio_links_endpoint(request: Request, payload: PortfolioLinksRequest):
    """
    Audits digital profile links (LinkedIn, GitHub, portfolio) for HTTPS security and placeholder patterns.
    """
    try:
        result = audit_portfolio_links(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit portfolio links endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit portfolio links: {str(err)}")

@app.post("/api/pdf-layout-tokens")
@limiter.limit("30/minute")
async def extract_pdf_layout_tokens_endpoint(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Extracts spatial layout tokens, normalized bounding boxes, and simulated
    recruiter eye-tracking gaze weights directly from an uploaded PDF.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Layout token extraction is only supported for PDF files.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES / (1024*1024):.0f}MB.")

    result = extract_pdf_layout_tokens(contents)
    if not result.get("success", False):
        raise HTTPException(status_code=422, detail=result.get("error", "Failed to parse PDF layout tokens."))

    return result

@app.post("/api/scrape-jd")
@limiter.limit("20/minute")
async def scrape_job_description_endpoint(request: Request, payload: ScrapeJobDescriptionRequest):
    """
    Fetches, sanitizes, and extracts structured requirements, company name,
    job title, and technical skills from target job URLs with SSRF protection.
    """
    try:
        result = await scrape_job_description(payload.url)
        if not result.get("success", False):
            raise HTTPException(status_code=422, detail=result.get("error", "Failed to scrape job description."))
        return result
    except ValueError as val_err:
        logger.warning(f"URL validation failed for {payload.url}: {val_err}")
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"Error scraping job description: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to process job URL: {str(err)}")

@app.post("/api/simulate-ats")
@limiter.limit("30/minute")
def simulate_ats_endpoint(request: Request, payload: SimulateATSRequest):
    """
    Simulates parsing behavior across Workday, Greenhouse/Lever, and Taleo/Oracle ATS engines,
    providing comparative diffs, entity extraction health, and cross-ATS hazard alerts.
    """
    try:
        result = run_multi_ats_simulation(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in multi-ATS simulation endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate ATS parsing: {str(err)}")

@app.post("/api/interview-prep")
@limiter.limit("20/minute")
async def generate_interview_prep_endpoint(request: Request, payload: InterviewPrepRequest):
    """
    Generates the top 5 toughest technical and behavioral probing interview questions
    with tailored STAR response strategies based on resume vulnerabilities and target JD gaps.
    """
    try:
        result = await generate_interview_prep(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            seniority=payload.seniority
        )
        return result
    except Exception as err:
        logger.error(f"Error in interview prep generation endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to generate interview preparation: {str(err)}")

@app.post("/api/resume/parse-structured")
@limiter.limit("30/minute")
def parse_structured_resume_endpoint(request: Request, payload: ParseStructuredResumeRequest):
    """
    Parses unstructured resume text into a structured, editable JSON schema.
    """
    try:
        result = parse_resume_to_structured_json(payload.resume_text)
        return {"structured_resume": result}
    except Exception as err:
        logger.error(f"Error parsing structured resume: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to parse structured resume: {str(err)}")

@app.post("/api/resume/format-clean-txt")
@limiter.limit("60/minute")
def format_clean_txt_endpoint(request: Request, payload: FormatCleanTxtRequest):
    """
    Converts structured resume data into clean, single-column ATS-safe plain text.
    """
    try:
        plain_text = format_structured_resume_to_plain_text(payload.structured_resume)
        return {"plain_text": plain_text}
    except Exception as err:
        logger.error(f"Error formatting structured resume to text: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to format resume text: {str(err)}")

@app.post("/api/generate-outreach")
@limiter.limit("20/minute")
async def generate_outreach_endpoint(request: Request, payload: GenerateOutreachRequest):
    """
    Generates personalized Cover Letters, LinkedIn InMails, Hiring Manager Cold Emails,
    and Follow-Up notes based on candidate resume and job requirements.
    """
    try:
        result = await generate_outreach(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            mode=payload.mode or "cover_letter",
            tone=payload.tone or "confident",
            recipient_name=payload.recipient_name,
            company_name=payload.company_name
        )
        return result
    except Exception as err:
        logger.error(f"Error generating outreach copy: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to generate outreach copy: {str(err)}")











