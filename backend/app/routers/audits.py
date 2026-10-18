import logging
from fastapi import APIRouter, HTTPException, Request

from app.limiter import limiter
from app.viewport import audit_first_third_viewport
from app.acronyms import expand_technical_terms
from app.header_normalizer import audit_section_headers
from app.token_density import audit_token_density
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
from app.summary_classifier import classify_summary_style
from app.salary_detector import detect_salary_disclosures
from app.portfolio_validator import audit_portfolio_links
from app.semantic_match import calculate_semantic_alignment
from app.dialect_checker import audit_dialect_and_voice
from app.skill_decay import profile_skill_decay
from app.role_readiness import evaluate_role_readiness
from app.compensation_calibrator import calibrate_compensation
from app.metric_consistency import audit_metric_verifiability
from app.education_hierarchy import parse_education_hierarchy
from app.cognitive_load import evaluate_cognitive_load
from app.leadership_scorer import profile_leadership_trajectory

from app.schemas import (
    ViewportAuditRequest,
    AcronymExpansionRequest,
    AuditHeadersRequest,
    TokenDensityRequest,
    SeniorityProfileRequest,
    RedactPIIRequest,
    LayoutAuditRequest,
    ChronologyAuditRequest,
    FontIntegrityRequest,
    BM25AuditRequest,
    ContactAuditRequest,
    SkillClassifyRequest,
    SectionFlowRequest,
    ActionVerbRequest,
    PageBudgetRequest,
    ReadabilityRequest,
    VoiceAuditRequest,
    ClicheAuditRequest,
    MetricDiversityRequest,
    FilenameAuditRequest,
    SkillRecencyRequest,
    SummaryStyleRequest,
    SalaryAuditRequest,
    PortfolioLinksRequest,
    SemanticMatchRequest,
    DialectConsistencyRequest,
    SkillDecayRequest,
    RoleReadinessRequest,
    CompensationCalibrationRequest,
    MetricConsistencyRequest,
    EducationHierarchyRequest,
    CognitiveLoadRequest,
    LeadershipProfileRequest,
)

router = APIRouter(tags=["Deterministic Audits & Heuristics"])
logger = logging.getLogger("ResumeAnalyserAPI.Audits")


@router.post("/api/viewport-audit")
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


@router.post("/api/expand-keywords")
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


@router.post("/api/audit-headers")
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


@router.post("/api/token-density")
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


@router.post("/api/seniority-profile")
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


@router.post("/api/redact-pii")
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


@router.post("/api/audit-layout")
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


@router.post("/api/audit-chronology")
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


@router.post("/api/audit-font-integrity")
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


@router.post("/api/audit-bm25")
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


@router.post("/api/audit-contact")
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


@router.post("/api/classify-skills")
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


@router.post("/api/audit-section-flow")
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


@router.post("/api/audit-action-verbs")
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


@router.post("/api/audit-page-budget")
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


@router.post("/api/audit-readability")
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


@router.post("/api/audit-voice")
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


@router.post("/api/audit-cliches")
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


@router.post("/api/audit-metric-diversity")
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


@router.post("/api/audit-filename")
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


@router.post("/api/audit-skill-recency")
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


@router.post("/api/audit-summary-style")
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


@router.post("/api/audit-salary-disclosures")
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


@router.post("/api/audit-portfolio-links")
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


@router.post("/api/semantic-match")
@limiter.limit("60/minute")
def semantic_match_endpoint(request: Request, payload: SemanticMatchRequest):
    """
    Computes Jaccard n-gram similarity, term recall, and semantic alignment
    between resume text and target job description.
    """
    try:
        return calculate_semantic_alignment(payload.resume_text, payload.job_description)
    except Exception as err:
        logger.error(f"Error computing semantic match: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate semantic match: {str(err)}")


@router.post("/api/audit/dialect-consistency")
@limiter.limit("60/minute")
def audit_dialect_consistency_endpoint(request: Request, payload: DialectConsistencyRequest):
    """
    Evaluates regional English dialect consistency (US vs UK) and passive voice density.
    """
    try:
        return audit_dialect_and_voice(payload.resume_text)
    except Exception as err:
        logger.error(f"Error checking dialect consistency: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit dialect consistency: {str(err)}")


@router.post("/api/audit/skill-decay")
@limiter.limit("60/minute")
def audit_skill_decay_endpoint(request: Request, payload: SkillDecayRequest):
    """
    Evaluates exponential half-life decay and technical skill freshness.
    """
    try:
        return profile_skill_decay(payload.resume_text, reference_year=payload.reference_year)
    except Exception as err:
        logger.error(f"Error profiling skill decay: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to profile skill decay: {str(err)}")


@router.post("/api/audit/role-readiness")
@router.post("/api/evaluate/role-readiness")
@limiter.limit("60/minute")
def audit_role_readiness_endpoint(request: Request, payload: RoleReadinessRequest):
    """
    Evaluates qualification coverage against standard industry job archetypes.
    """
    try:
        return evaluate_role_readiness(payload.resume_text, target_role=payload.target_role)
    except Exception as err:
        logger.error(f"Error evaluating role readiness: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate role readiness: {str(err)}")


@router.post("/api/audit/compensation-calibration")
@router.post("/api/calibrate/compensation")
@limiter.limit("60/minute")
def audit_compensation_calibration_endpoint(request: Request, payload: CompensationCalibrationRequest):
    """
    Calibrates candidate market seniority tier (L3-L7) and compensation bands.
    """
    try:
        return calibrate_compensation(payload.resume_text, years_experience=payload.years_experience)
    except Exception as err:
        logger.error(f"Error calibrating compensation: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to calibrate compensation: {str(err)}")


@router.post("/api/audit/metric-consistency")
@router.post("/api/audit/metric-verifiability")
@limiter.limit("60/minute")
def audit_metric_consistency_endpoint(request: Request, payload: MetricConsistencyRequest):
    """
    Audits resume text for numerical metric verifiability, implausible claims, and baseline denominator attachment.
    """
    try:
        return audit_metric_verifiability(payload.resume_text)
    except Exception as err:
        logger.error(f"Error auditing metric consistency: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to audit metric consistency: {str(err)}")


@router.post("/api/audit/education-hierarchy")
@router.post("/api/parse/education-hierarchy")
@limiter.limit("60/minute")
def audit_education_hierarchy_endpoint(request: Request, payload: EducationHierarchyRequest):
    """
    Parses educational credentials, degree hierarchy tiers, honors, and normalizes GPA scales.
    """
    try:
        return parse_education_hierarchy(payload.resume_text)
    except Exception as err:
        logger.error(f"Error parsing education hierarchy: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to parse education hierarchy: {str(err)}")


@router.post("/api/audit/cognitive-load")
@limiter.limit("60/minute")
def audit_cognitive_load_endpoint(request: Request, payload: CognitiveLoadRequest):
    """
    Evaluates Gunning Fog, Coleman-Liau, ARI, and recruiter glance cognitive load.
    """
    try:
        return evaluate_cognitive_load(payload.resume_text)
    except Exception as err:
        logger.error(f"Error evaluating cognitive load: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate cognitive load: {str(err)}")


@router.post("/api/audit/leadership-profile")
@router.post("/api/profile/leadership-trajectory")
@limiter.limit("60/minute")
def audit_leadership_profile_endpoint(request: Request, payload: LeadershipProfileRequest):
    """
    Profiles leadership competencies, scope of influence, and mapped organizational seniority tiers.
    """
    try:
        return profile_leadership_trajectory(payload.resume_text)
    except Exception as err:
        logger.error(f"Error profiling leadership trajectory: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to profile leadership trajectory: {str(err)}")
