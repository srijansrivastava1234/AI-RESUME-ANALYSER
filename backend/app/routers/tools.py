import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Request

from app.limiter import limiter
from app.agent_prompt import generate_agent_refactor_prompt
from app.jd_scraper import scrape_job_description
from app.interview_prep import generate_interview_prep
from app.resume_builder import parse_resume_to_structured_json, format_structured_resume_to_plain_text
from app.outreach import generate_outreach
from app.pdf_layout import extract_pdf_layout_tokens
from app.spatial_budgeter import audit_canvas_spatial_budget
from app.schemas import (
    AgentPromptRequest,
    ScrapeJobDescriptionRequest,
    InterviewPrepRequest,
    ParseStructuredResumeRequest,
    FormatCleanTxtRequest,
    GenerateOutreachRequest,
    SpatialBudgetRequest,
)

router = APIRouter(tags=["Career & Document Tools"])
logger = logging.getLogger("ResumeAnalyserAPI.Tools")

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


@router.post("/api/agent-prompt")
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


@router.post("/api/scrape-jd")
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


@router.post("/api/interview-prep")
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


@router.post("/api/resume/parse-structured")
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


@router.post("/api/resume/format-clean-txt")
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


@router.post("/api/generate-outreach")
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


@router.post("/api/pdf-layout-tokens")
@router.post("/api/v1/pdf/layout-tokens")
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

    file.file.seek(0, 2)
    f_size = file.file.tell()
    file.file.seek(0)
    if f_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.")

    contents = await file.read()

    result = extract_pdf_layout_tokens(contents)
    if not result.get("success", False):
        raise HTTPException(status_code=422, detail=result.get("error", "Failed to parse PDF layout tokens."))

    return result


@router.post("/api/layout/spatial-budget")
@limiter.limit("60/minute")
def audit_spatial_budget_endpoint(request: Request, payload: SpatialBudgetRequest):
    """
    Audits 2D Euclidean bounding box spatial density, margins, and gutter collisions.
    """
    try:
        fmt = payload.page_format if payload.page_format else "letter"
        margin = payload.min_margin_pt if payload.min_margin_pt is not None else 36.0
        return audit_canvas_spatial_budget(payload.boxes, page_format=fmt, min_margin_pt=margin)
    except Exception as err:
        logger.error(f"Error auditing spatial budget: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit spatial budget: {str(err)}")
