import logging
import time
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from slowapi.util import get_remote_address

from app.limiter import limiter
from app.parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from app.analyzer import analyze_resume
from app.comparator import compare_resumes
from app.hygiene import audit_resume_hygiene
from app.compliance import audit_ats_compliance
from app.agent_prompt import generate_agent_refactor_prompt
from app.layout_linearizer import simulate_recursive_xy_cut
from app.chronology import audit_career_chronology
from app.font_integrity import audit_font_cmap_integrity
from app.bm25_scorer import compute_bm25_plus
from app.contact_validator import audit_candidate_contact
from app.skill_classifier import audit_skills

router = APIRouter(tags=["Analysis & Ingestion"])
logger = logging.getLogger("ResumeAnalyserAPI.Analysis")

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_COMPARE_FILES = 5


@router.post("/api/analyze")
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
        
        file_bytes = await file.read()
        
        # 1. Parse text based on format (preserve raw layout text for XY-cut multi-column analysis)
        parse_start = time.time()
        page_count = None
        if filename_lower.endswith(".pdf"):
            extracted_text, page_count = extract_text_from_pdf(file_bytes)
            raw_layout_text, _ = extract_text_from_pdf(file_bytes, preserve_layout=True)
        elif filename_lower.endswith(".docx"):
            extracted_text = extract_text_from_docx(file_bytes)
            raw_layout_text = extract_text_from_docx(file_bytes, preserve_layout=True)
        else:
            extracted_text = extract_text_from_txt(file_bytes)
            raw_layout_text = extract_text_from_txt(file_bytes, preserve_layout=True)
            
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
        analysis_report["layout_linearization"] = simulate_recursive_xy_cut(raw_layout_text)
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
        
    except HTTPException:
        raise
    except ValueError as val_err:
        logger.warning(f"[{request_id}] Validation issue: {str(val_err)}")
        raise HTTPException(status_code=400, detail=str(val_err))
        
    except Exception as e:
        logger.error(f"[{request_id}] Error during resume analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )


@router.post("/api/compare")
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
            file.file.seek(0, 2)
            f_size = file.file.tell()
            file.file.seek(0)
            if f_size > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"File '{file.filename}' exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
                )

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

    except HTTPException:
        raise
    except ValueError as val_err:
        logger.warning(f"[{request_id}] Comparison validation: {str(val_err)}")
        raise HTTPException(status_code=400, detail=str(val_err))

    except Exception as e:
        logger.error(f"[{request_id}] Error during comparison: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during resume comparison: {str(e)}"
        )


@router.post("/api/hygiene")
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
        file.file.seek(0, 2)
        f_size = file.file.tell()
        file.file.seek(0)
        if f_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )

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
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"[{request_id}] Error in hygiene endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit hygiene: {str(err)}")
