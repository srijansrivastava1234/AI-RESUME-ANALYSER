"""
Module: section_order_validator.py
Purpose: Audits the hierarchical order of sections in a resume against standard
ATS optical flow: Contact -> Summary -> Experience -> Skills -> Education.
"""

from typing import List, Dict, Any

CANONICAL_ORDER = [
    "CONTACT",
    "SUMMARY",
    "EXPERIENCE",
    "SKILLS",
    "EDUCATION"
]

SECTION_SYNONYMS = {
    "CONTACT": ["contact", "header", "personal info"],
    "SUMMARY": ["summary", "professional summary", "about", "profile", "overview"],
    "EXPERIENCE": ["experience", "work experience", "employment", "work history", "professional experience"],
    "SKILLS": ["skills", "technical skills", "technologies", "competencies", "core competencies"],
    "EDUCATION": ["education", "academic background", "degrees", "certifications"]
}


def normalize_section_type(raw_name: str) -> str:
    """Map a raw section header name to its canonical section category."""
    raw_clean = raw_name.lower().strip()
    for cat, syns in SECTION_SYNONYMS.items():
        if any(s in raw_clean for s in syns):
            return cat
    return "OTHER"


def audit_section_order(section_names: List[str]) -> Dict[str, Any]:
    """
    Evaluates whether the order of resume sections follows standard ATS convention.
    """
    normalized = [normalize_section_type(s) for s in section_names]
    recognized = [n for n in normalized if n in CANONICAL_ORDER]

    # Check for experience appearing before summary or contact
    violations = []
    
    if "EDUCATION" in recognized and "EXPERIENCE" in recognized:
        edu_idx = recognized.index("EDUCATION")
        exp_idx = recognized.index("EXPERIENCE")
        # If Education precedes Experience and candidate is not a new grad
        if edu_idx < exp_idx:
            violations.append("Education appears before Experience (standard experienced profiles prioritize Experience).")

    # Check for Contact position
    if "CONTACT" in recognized and recognized.index("CONTACT") != 0:
        violations.append("Contact information should always be the top-most section.")

    is_compliant = len(violations) == 0
    score = 100 if is_compliant else max(50, 100 - len(violations) * 25)

    return {
        "raw_sections": section_names,
        "normalized_sequence": normalized,
        "is_compliant": is_compliant,
        "score": score,
        "violations": violations,
        "canonical_recommendation": CANONICAL_ORDER
    }
