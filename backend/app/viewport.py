"""
Recruiter 6-Second First-Third (Upper 30% Viewport) Precision Auditor.

Grounded in recruiter eye-tracking research (Ladders 2018 eye-tracking study)
and the ATS Validator Architecture:
- The human recruiter spends an average of 6.0 to 7.4 seconds during the initial scan.
- Recruiter attention is concentrated heavily within the First Third (upper 30%) of page 1.
- Evaluates whether high-impact metrics, active verbs, and target competencies
  are front-loaded or buried at the bottom of the document.
"""

import re
from typing import Dict, List, Any, Optional
from app.xyz_scorer import POWER_ACTION_VERBS, MEDIUM_ACTION_VERBS, METRIC_PATTERNS

ALL_ACTION_VERBS = POWER_ACTION_VERBS.union(MEDIUM_ACTION_VERBS)


def extract_metrics_from_text(text: str) -> List[str]:
    """
    Extracts numerical and scale metrics from input text using standardized regex patterns.
    """
    detected: List[str] = []
    for pattern in METRIC_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            metric_str = match.group(0).strip()
            if metric_str not in detected:
                detected.append(metric_str)
    return detected


def audit_first_third_viewport(
    raw_text: str,
    target_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyzes the upper 30% viewport of the resume against the remainder to evaluate
    recruiter 6-second scan readability and accomplishment front-loading.

    :param raw_text: Raw or parsed resume text.
    :param target_skills: Optional list of target technical skills to verify in upper viewport.
    :return: Dictionary containing viewport precision metrics, scores, and diagnostic advice.
    """
    if not raw_text or not raw_text.strip():
        return {
            "viewport_precision_score": 0,
            "status": "EMPTY_DOCUMENT",
            "total_words": 0,
            "viewport_words": 0,
            "viewport_metrics_count": 0,
            "remainder_metrics_count": 0,
            "front_loaded_metrics_ratio": 0.0,
            "viewport_verbs_count": 0,
            "detected_viewport_verbs": [],
            "detected_viewport_skills": [],
            "recommendations": ["Document is empty. Please provide resume text to audit."]
        }

    words = raw_text.split()
    total_words = len(words)

    if total_words < 30:
        return {
            "viewport_precision_score": 50,
            "status": "SHORT_DOCUMENT",
            "total_words": total_words,
            "viewport_words": total_words,
            "viewport_metrics_count": 0,
            "remainder_metrics_count": 0,
            "front_loaded_metrics_ratio": 1.0,
            "viewport_verbs_count": 0,
            "detected_viewport_skills": [],
            "recommendations": ["Resume is unusually short. Provide comprehensive work experience."]
        }

    # Partition document at 30% token boundary
    split_index = max(1, int(total_words * 0.30))
    viewport_tokens = words[:split_index]
    remainder_tokens = words[split_index:]

    viewport_text = " ".join(viewport_tokens)
    remainder_text = " ".join(remainder_tokens)

    # 1. Metrics detection in viewport vs remainder
    viewport_metrics = extract_metrics_from_text(viewport_text)
    remainder_metrics = extract_metrics_from_text(remainder_text)

    num_viewport_metrics = len(viewport_metrics)
    num_remainder_metrics = len(remainder_metrics)
    total_metrics = num_viewport_metrics + num_remainder_metrics

    front_loaded_ratio = (
        round(num_viewport_metrics / total_metrics, 2)
        if total_metrics > 0 else 0.0
    )

    # 2. Action verbs in viewport
    viewport_text_lower = viewport_text.lower()
    detected_viewport_verbs: List[str] = []
    for verb in ALL_ACTION_VERBS:
        pattern = r'\b' + re.escape(verb) + r'\b'
        if re.search(pattern, viewport_text_lower):
            detected_viewport_verbs.append(verb.title())

    detected_viewport_verbs = sorted(list(set(detected_viewport_verbs)))
    num_viewport_verbs = len(detected_viewport_verbs)

    # 3. Target skills detection in viewport
    detected_viewport_skills: List[str] = []
    if target_skills:
        for skill in target_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, viewport_text_lower):
                detected_viewport_skills.append(skill)

    # 4. Mathematical scoring of Viewport Precision (0-100)
    score = 50  # Baseline

    # Metric front-loading points (up to 30 pts)
    if num_viewport_metrics >= 3:
        score += 30
    elif num_viewport_metrics >= 2:
        score += 20
    elif num_viewport_metrics == 1:
        score += 10
    else:
        score -= 15

    # Action verb points (up to 20 pts)
    if num_viewport_verbs >= 4:
        score += 20
    elif num_viewport_verbs >= 2:
        score += 12
    elif num_viewport_verbs >= 1:
        score += 6
    else:
        score -= 10

    # Ratio bonus or penalty
    if total_metrics >= 3 and front_loaded_ratio < 0.20:
        score -= 20

    viewport_precision_score = max(0, min(100, score))

    # Status classification
    if viewport_precision_score >= 80:
        status = "EXCELLENT_PRECISION"
    elif viewport_precision_score >= 60:
        status = "ADEQUATE"
    else:
        status = "BACK_LOADED_RISK"

    # Actionable diagnostic recommendations
    recommendations: List[str] = []
    if num_viewport_metrics == 0:
        recommendations.append(
            "Recruiter 6-Second Alert: Zero quantifiable metrics detected in the upper 30% viewport. "
            "Front-load at least 2 measurable business outcomes (%, $, latency, scale) into your first role."
        )
    elif front_loaded_ratio < 0.25 and total_metrics >= 3:
        recommendations.append(
            f"Accomplishment Burying Warning: Only {num_viewport_metrics} of your {total_metrics} metrics "
            "appear in the first third. Elevate your strongest achievements to the top 3 bullets."
        )

    if num_viewport_verbs < 2:
        recommendations.append(
            "Action Verb Deficit: Upper viewport contains fewer than 2 active leadership verbs. "
            "Begin top bullets with assertive verbs (e.g., 'Architected', 'Spearheaded', 'Optimized')."
        )

    if not recommendations:
        recommendations.append(
            "High Precision: Key achievements and active verbs are prominently front-loaded for immediate recruiter impact."
        )

    return {
        "viewport_precision_score": viewport_precision_score,
        "status": status,
        "total_words": total_words,
        "viewport_words": len(viewport_tokens),
        "viewport_metrics_count": num_viewport_metrics,
        "remainder_metrics_count": num_remainder_metrics,
        "front_loaded_metrics_ratio": front_loaded_ratio,
        "viewport_verbs_count": num_viewport_verbs,
        "detected_viewport_verbs": detected_viewport_verbs[:5],
        "detected_viewport_skills": detected_viewport_skills,
        "recommendations": recommendations
    }
