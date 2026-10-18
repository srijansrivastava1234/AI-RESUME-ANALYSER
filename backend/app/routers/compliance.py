import logging
from fastapi import APIRouter, HTTPException, Request

from app.limiter import limiter
from app.compliance import audit_ats_compliance
from app.adverse_impact import audit_group_selection_rates
from app.hack_detector import detect_ats_hacks
from app.adversarial_steganography import sanitize_adversarial_text
from app.eeoc_statistical_auditor import generate_nyc_ll144_audit_report
from app.prompt_injection_detector import audit_prompt_injection_safety
from app.schemas import (
    ComplianceAuditRequest,
    AdverseImpactRequest,
    DetectHacksRequest,
    AdversarialAuditRequest,
    EeocAuditRequest,
    PromptInjectionAuditRequest,
)

router = APIRouter(tags=["Compliance & Security"])
logger = logging.getLogger("ResumeAnalyserAPI.Compliance")


@router.post("/api/compliance-audit")
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


@router.post("/api/adverse-impact")
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


@router.post("/api/detect-hacks")
@limiter.limit("30/minute")
def detect_hacks_endpoint(request: Request, payload: DetectHacksRequest):
    """
    Audits resume text for adversarial ATS manipulation, white-font keyword stuffing,
    invisible Unicode sequences, and CSS layout hiding traps.
    """
    try:
        result = detect_ats_hacks(payload.text, payload.raw_markup)
        return result
    except Exception as err:
        logger.error(f"Error in detect hacks endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to detect ATS hacks: {str(err)}")


@router.post("/api/audit/prompt-injection")
@router.post("/api/security/prompt-injection")
@limiter.limit("60/minute")
def audit_prompt_injection_endpoint(request: Request, payload: PromptInjectionAuditRequest):
    """
    Scans resume text for adversarial LLM prompt injections, hidden HTML comments, and zero-width steganography.
    """
    try:
        return audit_prompt_injection_safety(payload.resume_text)
    except Exception as err:
        logger.error(f"Error auditing prompt injection safety: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit prompt injection safety: {str(err)}")


@router.post("/api/security/adversarial-audit")
@limiter.limit("60/minute")
def audit_adversarial_security_endpoint(request: Request, payload: AdversarialAuditRequest):
    """
    Audits resume text for binary zero-width steganography and homoglyph attacks.
    """
    try:
        sanitized_text, audit_report = sanitize_adversarial_text(payload.resume_text)
        return {
            "sanitized_text": sanitized_text,
            "report": audit_report
        }
    except Exception as err:
        logger.error(f"Error auditing adversarial security: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit adversarial security: {str(err)}")


@router.post("/api/compliance/eeoc-audit")
@limiter.limit("60/minute")
def audit_eeoc_compliance_endpoint(request: Request, payload: EeocAuditRequest):
    """
    Audits candidate cohort selection rates under EEOC 4/5ths Rule and NYC LL 144.
    """
    try:
        threshold = payload.scoring_threshold if payload.scoring_threshold is not None else 70.0
        return generate_nyc_ll144_audit_report(payload.cohort_data, scoring_threshold=threshold)
    except Exception as err:
        logger.error(f"Error performing EEOC compliance audit: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit EEOC compliance: {str(err)}")
