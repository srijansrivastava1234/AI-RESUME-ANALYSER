"""
Module: schemas.py
Purpose: Pydantic V2 schema models and typed contracts for API requests, responses,
and ATS audit payloads.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class OptimizeBulletPayload(BaseModel):
    bullet: str = Field(..., min_length=5, description="The resume bullet point text to optimize")
    target_role: Optional[str] = Field(None, description="Optional target job title or role context")


class ScoreBulletPayload(BaseModel):
    bullet: str = Field(..., min_length=1, description="The resume bullet point text to evaluate")
    seniority: Optional[str] = Field("mid", description="Seniority tier: junior, mid, senior, staff, executive")


class ComplianceAuditPayload(BaseModel):
    resume_text: str = Field(..., min_length=10, description="The plain text of the resume to audit")
    job_description: Optional[str] = Field(None, description="Optional target job description")
    seniority: Optional[str] = Field("mid", description="Seniority tier")
    target_pages: Optional[int] = Field(1, description="Expected page budget: 1 or 2 pages")


class ScrapeJdPayload(BaseModel):
    url: str = Field(..., description="Target job description posting URL (http or https)")


class SimulateAtsPayload(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Resume text to run across Workday, Greenhouse, and Taleo parsers")


class InterviewPrepPayload(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Resume plain text")
    job_description: Optional[str] = Field(None, description="Optional target job description")
    seniority: Optional[str] = Field("mid", description="Target seniority tier")
    target_role: Optional[str] = Field(None, description="Optional target role name")


class GenerateOutreachPayload(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Candidate resume text")
    job_description: Optional[str] = Field(None, description="Target job description")
    outreach_type: str = Field("cover_letter", description="Outreach format: cover_letter, linkedin_inmail, hiring_manager_email, follow_up")
    tone: Optional[str] = Field("confident", description="Tone: confident, direct, technical, executive")


class HealthResponse(BaseModel):
    status: str = Field("healthy", description="System health status")
    version: str = Field(..., description="Application semantic version")
    service: str = Field("AI Resume Analyser API", description="Service identifier")
    supported_formats: List[str] = Field(default=["pdf", "docx", "txt"], description="Supported file formats")
    max_file_size_mb: int = Field(10, description="Maximum upload size limit in MB")


class DiagnosticsResponse(BaseModel):
    status: str = Field(..., description="System operational status")
    version: str = Field(..., description="API semantic version")
    environment: Dict[str, Any] = Field(..., description="Runtime environment attributes")
    engines: Dict[str, Any] = Field(..., description="Loaded ATS simulation and scoring engines")
    compliance: Dict[str, str] = Field(..., description="Active regulatory frameworks")


# ==============================================================================
# Unified API Endpoint Request Models
# ==============================================================================

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

class SemanticMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="The plain text of the candidate resume")
    job_description: str = Field(..., min_length=5, description="Target job description plain text")

class BulletTypographyRequest(BaseModel):
    bullets: List[str] = Field(..., min_length=1, description="List of resume bullet points to audit for typography and typos")

class ATSBenchmarkRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Plain text of the candidate resume")

class DialectConsistencyRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to evaluate for dialect and grammatical voice consistency")

class SkillDecayRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to profile for technical skill freshness and half-life decay")
    reference_year: Optional[int] = Field(None, description="Optional baseline year for decay calculations")

class RoleReadinessRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Candidate resume text to evaluate against target archetypes")
    target_role: Optional[str] = Field(None, description="Target archetype key ('backend_engineer', 'frontend_engineer', 'fullstack_engineer', 'ml_engineer', 'devops_platform_engineer', 'data_engineer')")

class CompensationCalibrationRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Candidate resume text to calibrate for seniority tier and compensation bands")
    years_experience: Optional[float] = Field(None, description="Optional explicit total years of experience")

class MetricConsistencyRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to evaluate for metric verifiability and baseline denominator calibration")

class EducationHierarchyRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text or education section to parse and evaluate academic hierarchy")

class CognitiveLoadRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to evaluate for cognitive load, Gunning Fog, and recruiter skimmability")

class PromptInjectionAuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to audit for adversarial prompt injections, steganography, and security risks")

class LeadershipProfileRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to profile for leadership competencies, scope, and seniority tier")

class AtsSimulatorRequest(BaseModel):
    resume_text: str = Field(..., min_length=5, description="Resume text to simulate across ATS parsing engines")

class AdversarialAuditRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text to audit for steganography and homoglyph attacks")

class EeocAuditRequest(BaseModel):
    cohort_data: Dict[str, Dict[str, Any]] = Field(..., description="Cohort selection and scoring counts")
    scoring_threshold: Optional[float] = Field(70.0, description="Minimum score threshold for candidate selection")

class SpatialBudgetRequest(BaseModel):
    boxes: List[Dict[str, Any]] = Field(..., description="List of bounding boxes on page canvas")
    page_format: Optional[str] = Field("letter", description="Canvas format ('letter' or 'a4')")
    min_margin_pt: Optional[float] = Field(36.0, description="Minimum margin in points")
