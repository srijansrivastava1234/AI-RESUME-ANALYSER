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
