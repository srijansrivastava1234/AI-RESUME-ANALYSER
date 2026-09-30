"""
Multi-Engine ATS Layout Hazard & Field Extraction Benchmarker.
Audits resume text against specific parsing failure modes across Workday,
Taleo (Oracle), Greenhouse/Lever, and iCIMS applicant tracking systems.
"""

import re
from typing import Dict, Any, List, Optional

STANDARD_SECTIONS = [
    "experience", "work experience", "professional experience", "employment history",
    "education", "academic background",
    "skills", "technical skills", "core competencies",
    "projects", "personal projects", "key projects",
    "certifications", "licenses"
]

def benchmark_ats_parsing_resilience(resume_text: str) -> Dict[str, Any]:
    """
    Simulates parsing behavior across Workday, Taleo, Greenhouse, and iCIMS.
    Returns composite score, engine breakdown, detected hazards, and actionable remediation.
    """
    if not resume_text or not resume_text.strip():
        return {
            "resilience_score": 0,
            "resilience_grade": "F",
            "detected_sections": [],
            "missing_critical_sections": ["Experience", "Education", "Skills"],
            "contact_detection": {
                "email_detected": False,
                "phone_detected": False,
                "linkedin_detected": False
            },
            "engine_breakdown": {
                "workday": {"score": 0, "status": "Failed", "hazards": ["Empty document"]},
                "taleo": {"score": 0, "status": "Failed", "hazards": ["Empty document"]},
                "greenhouse": {"score": 0, "status": "Failed", "hazards": ["Empty document"]},
                "icims": {"score": 0, "status": "Failed", "hazards": ["Empty document"]}
            },
            "recommendations": ["Provide non-empty resume text for ATS parsing simulation."]
        }

    text_lower = resume_text.lower()

    # 1. Section Header Detection
    detected_sections = []
    for sec in STANDARD_SECTIONS:
        pattern = rf"(?:^|\n)\s*{re.escape(sec)}\s*(?::|\n|$)"
        if re.search(pattern, text_lower, re.MULTILINE):
            detected_sections.append(sec.title())

    has_exp = any("experience" in s.lower() for s in detected_sections)
    has_edu = any("education" in s.lower() for s in detected_sections)
    has_skills = any("skill" in s.lower() for s in detected_sections)

    missing_critical = []
    if not has_exp:
        missing_critical.append("Experience")
    if not has_edu:
        missing_critical.append("Education")
    if not has_skills:
        missing_critical.append("Skills")

    # 2. Contact Information Detection
    email_match = bool(re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", resume_text))
    phone_match = bool(re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", resume_text))
    linkedin_match = bool(re.search(r"linkedin\.com/in/[a-zA-Z0-9_-]+", resume_text, re.IGNORECASE))
    github_match = bool(re.search(r"github\.com/[a-zA-Z0-9_-]+", resume_text, re.IGNORECASE))

    # 3. Date Syntax & Chronology Format Verification
    date_patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
        r"\b\d{1,2}/\d{4}\b",
        r"\b(?:20\d{2}|19\d{2})\s*[-–—]\s*(?:20\d{2}|19\d{2}|Present|Current)\b"
    ]
    has_standard_dates = any(bool(re.search(p, resume_text, re.IGNORECASE)) for p in date_patterns)

    # 4. Engine-Specific Hazard Analysis
    # Workday: Sensitive to missing contact headers, unstructured chronological blocks
    workday_hazards = []
    workday_score = 100
    if not email_match or not phone_match:
        workday_hazards.append("Workday may fail to auto-populate candidate profile without explicit Email/Phone.")
        workday_score -= 25
    if not has_exp:
        workday_hazards.append("Workday career timeline parser requires standard 'Work Experience' header.")
        workday_score -= 30
    if not has_standard_dates:
        workday_hazards.append("Non-standard date formats may cause overlapping role extraction errors in Workday.")
        workday_score -= 15

    # Taleo: Sensitive to non-ASCII characters, table/column delimiters
    taleo_hazards = []
    taleo_score = 100
    non_ascii_count = len(re.findall(r"[^\x00-\x7F]", resume_text))
    if non_ascii_count > 15:
        taleo_hazards.append(f"Found {non_ascii_count} non-ASCII characters which frequently garble in Taleo parsers.")
        taleo_score -= 20
    if not has_exp or not has_skills:
        taleo_hazards.append("Taleo strict ontology matcher requires explicit 'Experience' and 'Skills' section anchors.")
        taleo_score -= 30
    if "|" in resume_text:
        pipe_count = resume_text.count("|")
        if pipe_count > 8:
            taleo_hazards.append("Heavy pipe (|) delimiter usage can disrupt Taleo single-column text flow.")
            taleo_score -= 10

    # Greenhouse/Lever: Modern, tolerant but requires clean Markdown/Plain Text structure
    gh_hazards = []
    gh_score = 100
    if not email_match:
        gh_hazards.append("Greenhouse requires valid email address for candidate profile creation.")
        gh_score -= 30
    if not has_skills and not has_exp:
        gh_hazards.append("Missing standard section headers lowers candidate scorecard indexing in Greenhouse.")
        gh_score -= 25

    # iCIMS: Sensitive to nested headers and multi-line titles
    icims_hazards = []
    icims_score = 100
    if not has_standard_dates:
        icims_hazards.append("iCIMS tenure calculation engine requires consistent 'Month Year - Present' format.")
        icims_score -= 20
    if len(missing_critical) > 0:
        icims_hazards.append(f"Missing core section(s): {', '.join(missing_critical)} disrupts iCIMS parsing.")
        icims_score -= (15 * len(missing_critical))

    workday_score = max(min(workday_score, 100), 0)
    taleo_score = max(min(taleo_score, 100), 0)
    gh_score = max(min(gh_score, 100), 0)
    icims_score = max(min(icims_score, 100), 0)

    composite_score = round(
        (workday_score * 0.35) +
        (taleo_score * 0.25) +
        (gh_score * 0.25) +
        (icims_score * 0.15)
    )

    if composite_score >= 90:
        grade = "A+"
    elif composite_score >= 80:
        grade = "A"
    elif composite_score >= 70:
        grade = "B"
    elif composite_score >= 60:
        grade = "C"
    else:
        grade = "F"

    # Actionable Recommendations
    recommendations = []
    if missing_critical:
        recommendations.append(f"Add standard section headers for: {', '.join(missing_critical)}.")
    if not email_match or not phone_match:
        recommendations.append("Ensure email and phone number are clearly visible at top of resume.")
    if not has_standard_dates:
        recommendations.append("Adopt standardized date format: 'Month YYYY – Present' (e.g. 'Jan 2022 – Present').")
    if non_ascii_count > 15:
        recommendations.append("Replace special symbols or decorative glyphs with standard ASCII bullet points.")

    if not recommendations:
        recommendations.append("Document demonstrates excellent multi-engine ATS parsing resilience.")

    return {
        "resilience_score": composite_score,
        "resilience_grade": grade,
        "detected_sections": detected_sections,
        "missing_critical_sections": missing_critical,
        "contact_detection": {
            "email_detected": email_match,
            "phone_detected": phone_match,
            "linkedin_detected": linkedin_match,
            "github_detected": github_match
        },
        "engine_breakdown": {
            "workday": {
                "score": workday_score,
                "status": "Optimal" if workday_score >= 80 else ("Moderate" if workday_score >= 60 else "High Risk"),
                "hazards": workday_hazards
            },
            "taleo": {
                "score": taleo_score,
                "status": "Optimal" if taleo_score >= 80 else ("Moderate" if taleo_score >= 60 else "High Risk"),
                "hazards": taleo_hazards
            },
            "greenhouse": {
                "score": gh_score,
                "status": "Optimal" if gh_score >= 80 else ("Moderate" if gh_score >= 60 else "High Risk"),
                "hazards": gh_hazards
            },
            "icims": {
                "score": icims_score,
                "status": "Optimal" if icims_score >= 80 else ("Moderate" if icims_score >= 60 else "High Risk"),
                "hazards": icims_hazards
            }
        },
        "recommendations": recommendations
    }
