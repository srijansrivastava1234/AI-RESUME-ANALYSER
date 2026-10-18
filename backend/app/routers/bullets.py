import logging
from fastapi import APIRouter, HTTPException, Request

from app.limiter import limiter
from app.xyz_scorer import score_resume_bullet, evaluate_bullet_verb_diversity
from app.rewriter import optimize_bullet_point
from app.metric_validator import audit_bullet_metrics
from app.bullet_length import analyze_bullet_lengths
from app.bullet_linter import audit_bullet_list_typography
from app.schemas import (
    ScoreBulletRequest,
    OptimizeBulletRequest,
    VerbDiversityRequest,
    ValidateMetricRequest,
    BulletLengthRequest,
    BulletTypographyRequest,
)

router = APIRouter(tags=["Bullet Intelligence & Scoring"])
logger = logging.getLogger("ResumeAnalyserAPI.Bullets")


@router.post("/api/score-bullet")
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


@router.post("/api/optimize-bullet")
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


@router.post("/api/verb-diversity")
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


@router.post("/api/validate-metric")
@limiter.limit("30/minute")
def validate_metric_endpoint(request: Request, payload: ValidateMetricRequest):
    """
    Audits a bullet statement for quantifiable business metrics and measurement denominators.
    """
    try:
        result = audit_bullet_metrics(payload.bullet)
        return result
    except Exception as err:
        logger.error(f"Error in validate metric endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to validate metric: {str(err)}")


@router.post("/api/audit-bullet-lengths")
@limiter.limit("30/minute")
def audit_bullet_lengths_endpoint(request: Request, payload: BulletLengthRequest):
    """
    Audits resume bullet statements for conciseness, line wrapping, and word count.
    """
    try:
        result = analyze_bullet_lengths(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in audit bullet lengths endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit bullet lengths: {str(err)}")


@router.post("/api/audit/bullet-typography")
@limiter.limit("60/minute")
def audit_bullet_typography_endpoint(request: Request, payload: BulletTypographyRequest):
    """
    Audits resume bullet points for spacing anomalies, unbalanced punctuation,
    common typos, and trailing period consistency.
    """
    try:
        return audit_bullet_list_typography(payload.bullets)
    except Exception as err:
        logger.error(f"Error auditing bullet typography: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit bullet typography: {str(err)}")
