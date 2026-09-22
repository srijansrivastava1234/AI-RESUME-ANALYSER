"""
Skill Recency & Timeline Tenure Decay Engine.
Analyzes temporal positioning of technical skills across a candidate's career chronology,
differentiating current active proficiencies from dormant or deprecated tech stacks.
"""

import re
from typing import Dict, Any, List, Set

LEGACY_DEPRECATED_TECH = {
    "angularjs", "angular 1", "flash", "actionscript", "silverlight", "coldfusion",
    "vb6", "visual basic 6", "coffeescript", "bower", "grunt", "gulp", "cvs",
    "subversion", "svn", "clearcase", "vss", "backbone.js", "knockout.js", "mootools"
}

MODERN_HIGH_VALUE_TECH = {
    "python", "react", "fastapi", "docker", "kubernetes", "typescript", "golang", "rust",
    "aws", "gcp", "azure", "postgresql", "kafka", "graphql", "terraform", "pytorch",
    "next.js", "langchain", "tailwind", "redis", "spark"
}


def analyze_skill_recency(resume_text: str, current_year: int = 2026) -> Dict[str, Any]:
    """
    Evaluates skill recency and temporal distribution across candidate career history.
    """
    if not resume_text or not resume_text.strip():
        return {
            "recency_score": 0.0,
            "active_skills": [],
            "dormant_skills": [],
            "legacy_skills": [],
            "status": "PASS",
            "feedback": ["Empty resume text."]
        }

    text_lower = resume_text.lower()
    
    # 1. Detect legacy/deprecated stacks
    legacy_found: List[str] = []
    for leg in LEGACY_DEPRECATED_TECH:
        if re.search(r'\b' + re.escape(leg) + r'\b', text_lower):
            legacy_found.append(leg)

    # 2. Extract modern tech stacks
    modern_found: List[str] = []
    for mod in MODERN_HIGH_VALUE_TECH:
        if re.search(r'\b' + re.escape(mod) + r'\b', text_lower):
            modern_found.append(mod)

    # 3. Detect experience blocks with years
    # Find all 4-digit years in the text (1990 - 2030)
    years = [int(y) for y in re.findall(r'\b(19\d\d|20\d\d)\b', resume_text)]
    max_year = max(years) if years else current_year
    min_year = min(years) if years else current_year

    has_current_role = bool(re.search(r'\b(?:present|current|now|ongoing)\b', text_lower) or (max_year >= current_year - 1))

    # Calculate temporal recency score
    base_score = 70.0
    if has_current_role:
        base_score += 15.0
    if len(modern_found) >= 4:
        base_score += 15.0
    elif len(modern_found) >= 2:
        base_score += 10.0

    # Penalty for legacy tech without modern counterparts
    if len(legacy_found) > 0 and len(modern_found) < len(legacy_found):
        base_score -= 20.0
    elif len(legacy_found) > 0:
        base_score -= (len(legacy_found) * 5.0)

    final_score = max(0.0, min(100.0, round(base_score, 1)))

    feedback: List[str] = []
    if final_score >= 85.0:
        status = "EXCELLENT"
        feedback.append(f"High technical recency. Contemporary stack ({len(modern_found)} modern frameworks/tools) actively aligned with current market demand.")
    elif final_score >= 70.0:
        status = "PASS"
        feedback.append("Good skill currency. Keep core tools at the top of your technical skills section.")
    else:
        status = "WARNING"
        feedback.append("Skill profile may look dated. Highlight contemporary cloud, framework, and AI tooling over legacy platforms.")

    if legacy_found:
        feedback.append(f"Legacy tools detected ({', '.join(legacy_found)}). Deprecate or relegate to an 'Additional Exposure' subsection.")

    return {
        "recency_score": final_score,
        "is_active_career": has_current_role,
        "latest_year_detected": max_year,
        "modern_skills_detected": modern_found,
        "legacy_skills_detected": legacy_found,
        "status": status,
        "feedback": feedback
    }
