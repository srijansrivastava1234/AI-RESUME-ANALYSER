"""
ATS Section Flow & Structural Ordering Auditor
Evaluates the sequential structure and ordering of resume sections against enterprise ATS
parsing heuristics and recruiter eye-tracking standards (F-pattern scan).
"""

import re
from typing import Dict, Any, List, Optional

# Standard recommended section orders
EXPERIENCED_PREFERRED_ORDER = [
    "Contact Info",
    "Professional Summary",
    "Work Experience",
    "Skills",
    "Projects",
    "Education",
    "Certifications",
]

EARLY_CAREER_PREFERRED_ORDER = [
    "Contact Info",
    "Professional Summary",
    "Education",
    "Skills",
    "Projects",
    "Work Experience",
    "Certifications",
]

SECTION_PATTERN_MAP = {
    "Contact Info": r"(?:contact|email|phone|linkedin|github|portfolio)",
    "Professional Summary": r"(?:summary|objective|profile|about\s+me|overview)",
    "Work Experience": r"(?:work\s+experience|professional\s+experience|experience|employment|work\s+history)",
    "Education": r"(?:education|academic|degrees|university)",
    "Skills": r"(?:skills|technical\s+skills|core\s+competencies|technologies)",
    "Projects": r"(?:projects|personal\s+projects|academic\s+projects|key\s+projects)",
    "Certifications": r"(?:certifications|certificates|licenses|accreditations)",
    "Hobbies": r"(?:hobbies|interests|extracurricular)",
}


def detect_detected_section_order(text: str) -> List[Dict[str, Any]]:
    """
    Detects section headers and their line/character positions in the resume text.
    """
    lines = text.split("\n")
    detected = []
    
    for idx, line in enumerate(lines):
        clean = line.strip().lower()
        if not clean or len(clean) > 45:
            continue
        
        # Check against patterns (line should look like a header: short, isolated)
        for section_name, pattern in SECTION_PATTERN_MAP.items():
            if re.fullmatch(pattern, clean) or (re.match(pattern, clean) and len(clean.split()) <= 4):
                # Avoid duplicate adjacent tags for same section
                if not detected or detected[-1]["section"] != section_name:
                    detected.append({
                        "section": section_name,
                        "line_number": idx + 1,
                        "raw_header": line.strip()
                    })
                break
                
    return detected


def audit_section_flow(text: str, is_early_career: bool = False) -> Dict[str, Any]:
    """
    Audits resume section sequence, identifying jarring inversions, misplaced sections,
    or buried core qualifications.
    """
    detected = detect_detected_section_order(text)
    detected_names = [d["section"] for d in detected]
    
    warnings: List[str] = []
    recommendations: List[str] = []
    penalties = 0
    
    preferred_order = EARLY_CAREER_PREFERRED_ORDER if is_early_career else EXPERIENCED_PREFERRED_ORDER
    
    # Check if Hobbies / Interests appears before Experience or Education
    if "Hobbies" in detected_names:
        hob_idx = detected_names.index("Hobbies")
        if "Work Experience" in detected_names and hob_idx < detected_names.index("Work Experience"):
            warnings.append("Low-signal 'Hobbies/Interests' section precedes 'Work Experience'. Move it to the bottom.")
            penalties += 25
        elif "Education" in detected_names and hob_idx < detected_names.index("Education"):
            warnings.append("Hobbies section appears before Core Education/Qualifications.")
            penalties += 20

    # For experienced professionals, Education before Work Experience is suboptimal
    if not is_early_career and "Education" in detected_names and "Work Experience" in detected_names:
        edu_idx = detected_names.index("Education")
        exp_idx = detected_names.index("Work Experience")
        if edu_idx < exp_idx:
            recommendations.append("For experienced candidates (>2 yrs), placing 'Work Experience' above 'Education' improves recruiter scanability.")
            penalties += 10

    # Check if Core Skills is missing or buried at the absolute end
    if "Skills" not in detected_names:
        warnings.append("No distinct 'Skills' section detected. ATS parsers rely heavily on dedicated skills blocks.")
        penalties += 20
    elif len(detected_names) >= 4 and detected_names[-1] == "Skills":
        recommendations.append("Skills section is positioned at the very bottom. Placing Skills near the top or after Experience enhances keyword indexing.")
        penalties += 5

    # Check if Work Experience is missing
    if "Work Experience" not in detected_names:
        warnings.append("No distinct 'Work Experience' section detected. This is a critical structural omission.")
        penalties += 35

    flow_score = max(0, 100 - penalties)
    
    return {
        "flow_score": flow_score,
        "is_optimal": flow_score >= 85,
        "detected_sequence": detected_names,
        "detected_sections_detail": detected,
        "warnings": warnings,
        "recommendations": recommendations,
        "benchmark_profile": "Early Career" if is_early_career else "Experienced Professional"
    }
