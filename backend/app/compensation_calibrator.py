"""
Market Seniority Tier & Compensation Band Calibrator.
Estimates candidate market level (L3 Junior through L7 Principal/Director),
projected base salary and total compensation (TC) bands, and high-leverage compensation boosters
based on leadership scope, system scale indicators, and quantified business impact metrics.
"""

import re
from typing import Dict, Any, List, Optional

TIER_BENCHMARKS = {
    "L3": {
        "title": "Junior Software Engineer (L3)",
        "min_years": 0,
        "max_years": 2,
        "base_range": (90000, 130000),
        "total_comp_range": (105000, 150000),
    },
    "L4": {
        "title": "Mid-Level Software Engineer (L4)",
        "min_years": 2,
        "max_years": 5,
        "base_range": (135000, 175000),
        "total_comp_range": (160000, 220000),
    },
    "L5": {
        "title": "Senior Software Engineer (L5)",
        "min_years": 5,
        "max_years": 8,
        "base_range": (175000, 225000),
        "total_comp_range": (230000, 330000),
    },
    "L6": {
        "title": "Staff Engineer / Tech Lead (L6)",
        "min_years": 8,
        "max_years": 12,
        "base_range": (220000, 280000),
        "total_comp_range": (350000, 520000),
    },
    "L7": {
        "title": "Principal Engineer / Director (L7)",
        "min_years": 12,
        "max_years": 30,
        "base_range": (270000, 350000),
        "total_comp_range": (550000, 850000),
    }
}

LEADERSHIP_PATTERNS = [
    r"\b(?:led|managed|spearheaded|orchestrated|mentored|coached|directed|guided)\b",
    r"\b(?:hiring|interviewing|roadmaps?|strategy|cross-functional|stakeholders?)\b",
    r"\b(?:team\s+of\s+\d+|squad\s+lead|tech\s+lead|engineering\s+manager)\b"
]

SCALE_PATTERNS = [
    r"\b(?:million|billion|petabyte|terabyte|qps|rps|tps|concurrent|distributed)\b",
    r"\b(?:high-throughput|low-latency|fault-tolerant|99\.99%|uptime|sla)\b",
    r"\b(?:multi-region|cluster|fleet|microservices|distributed\s+systems)\b"
]

IMPACT_METRIC_PATTERNS = [
    r"\b\d+%\b",
    r"\$[\d,]+(?:\.\d+)?(?:k|m|b)?\b",
    r"\b(?:reduced|saved|increased|accelerated|generated|boosted)\b"
]

def calibrate_compensation(
    resume_text: str,
    years_experience: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calibrates candidate market seniority tier and estimated compensation bands.
    """
    if not resume_text or not resume_text.strip():
        return {
            "seniority_tier": "L3",
            "tier_title": TIER_BENCHMARKS["L3"]["title"],
            "base_salary_median": 110000,
            "base_salary_range": "$90k – $130k",
            "total_compensation_median": 127500,
            "total_compensation_range": "$105k – $150k",
            "confidence_score": 50.0,
            "scope_multiplier": 1.0,
            "detected_signals": {
                "leadership_count": 0,
                "scale_indicators_count": 0,
                "quantified_metrics_count": 0
            },
            "compensation_levers": ["Provide resume text to calculate market compensation calibration."]
        }

    lower_text = resume_text.lower()

    # Detect signals
    leadership_matches = sum(len(re.findall(p, lower_text)) for p in LEADERSHIP_PATTERNS)
    scale_matches = sum(len(re.findall(p, lower_text)) for p in SCALE_PATTERNS)
    metric_matches = sum(len(re.findall(p, lower_text)) for p in IMPACT_METRIC_PATTERNS)

    # Estimate years of experience if not provided
    if years_experience is None:
        years = [int(y) for y in re.findall(r"\b(20\d\d|19\d\d)\b", resume_text)]
        if len(years) >= 2:
            years_experience = float(max(years) - min(years))
        else:
            years_experience = 3.0

    # Determine base tier
    if years_experience < 2:
        tier_key = "L3"
    elif years_experience < 5:
        tier_key = "L4"
    elif years_experience < 8:
        tier_key = "L5"
    elif years_experience < 12:
        tier_key = "L6"
    else:
        tier_key = "L7"

    # Adjust tier upward if candidate displays extraordinary leadership + scale signals
    if tier_key == "L4" and leadership_matches >= 4 and scale_matches >= 3:
        tier_key = "L5"
    elif tier_key == "L5" and leadership_matches >= 6 and scale_matches >= 5:
        tier_key = "L6"
    elif tier_key == "L6" and leadership_matches >= 10 and scale_matches >= 8:
        tier_key = "L7"

    benchmark = TIER_BENCHMARKS[tier_key]

    # Calculate scope bonus multiplier (up to +15% within tier)
    scope_bonus = min(0.15, (leadership_matches * 0.02) + (scale_matches * 0.02) + (metric_matches * 0.01))
    scope_multiplier = round(1.0 + scope_bonus, 2)

    base_min = int(benchmark["base_range"][0] * scope_multiplier)
    base_max = int(benchmark["base_range"][1] * scope_multiplier)
    base_median = int((base_min + base_max) / 2)

    tc_min = int(benchmark["total_comp_range"][0] * scope_multiplier)
    tc_max = int(benchmark["total_comp_range"][1] * scope_multiplier)
    tc_median = int((tc_min + tc_max) / 2)

    confidence = min(95.0, 60.0 + (metric_matches * 3.0) + (scale_matches * 2.0))

    levers = []
    if metric_matches < 4:
        levers.append("Quantify business outcomes ($ saved, % latency reduction) to validate top-of-band market pricing.")
    if leadership_matches < 3 and tier_key in ["L5", "L6", "L7"]:
        levers.append("Explicitly highlight cross-functional leadership, mentoring, and technical roadmap ownership.")
    if scale_matches < 3:
        levers.append("Detail production scale metrics (QPS, concurrent users, data volume) to prove architectural scope.")
    if not levers:
        levers.append(f"Strong signal profile: Positioning aligns with top-quartile {benchmark['title']} compensation.")

    return {
        "seniority_tier": tier_key,
        "tier_title": benchmark["title"],
        "estimated_years_exp": round(years_experience, 1),
        "base_salary_median": base_median,
        "base_salary_range": f"${base_min//1000}k – ${base_max//1000}k",
        "total_compensation_median": tc_median,
        "total_compensation_range": f"${tc_min//1000}k – ${tc_max//1000}k",
        "confidence_score": round(confidence, 1),
        "scope_multiplier": scope_multiplier,
        "detected_signals": {
            "leadership_count": leadership_matches,
            "scale_indicators_count": scale_matches,
            "quantified_metrics_count": metric_matches
        },
        "compensation_levers": levers
    }
