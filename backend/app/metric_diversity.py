"""
Metric Diversity Classifier for ATS & Executive Resumes.
Categorizes quantified achievements into Financial, Velocity/Latency, Scale/Volume,
Percentage Growth, and People/Leadership dimensions to measure outcome breadth.
"""

import re
from typing import Dict, Any, List

DIMENSION_PATTERNS = {
    "financial": [
        r'\$\s*\d+(?:\.\d+)?[kKmMbBtT]?(?:\s*(?:million|billion|thousand|USD|ARR|MRR|revenue|budget|savings))?',
        r'\b\d+(?:\.\d+)?\s*(?:million|billion|thousand)\s*(?:dollars|USD|budget|revenue|savings)\b'
    ],
    "percentage": [
        r'\b\d+(?:\.\d+)?%',
        r'\b\d+(?:\.\d+)?x\b',
        r'\b(?:increased|decreased|reduced|improved|boosted|grew)\s+by\s+\d+(?:\.\d+)?%\b'
    ],
    "scale_volume": [
        r'\b\d+(?:\.\d+)?[kKmMbB]?\+?\s*(?:users|daily\s+active|DAU|MAU|requests|QPS|RPS|transactions|records|events|devices|nodes|clusters|servers|GB|TB|PB)\b',
        r'\b(?:petabytes|terabytes|gigabytes)\b'
    ],
    "velocity_time": [
        r'\b\d+(?:\.\d+)?\s*(?:ms|milliseconds|seconds|mins|minutes|hours|days|weeks|months)\b',
        r'\b(?:reduced|accelerated|slashed|shortened)\s+(?:latency|deployment|cycle\s+time|turnaround|build\s+time)\s+by\s+\d+\b'
    ],
    "people_leadership": [
        r'\b(?:team|squad|group|cohort)\s+of\s+\d+\b',
        r'\b(?:mentored|managed|led|directed|onboarded|coached)\s+\d+\s*(?:engineers|developers|interns|analysts|reports|team\s+members)?\b'
    ]
}


def analyze_metric_diversity(text: str) -> Dict[str, Any]:
    """
    Evaluates metric diversity across 5 critical dimensions.
    High-performing resumes showcase metrics across at least 3 distinct categories.
    """
    if not text or not text.strip():
        return {
            "diversity_score": 0.0,
            "dimensions_covered": 0,
            "dimension_breakdown": {k: [] for k in DIMENSION_PATTERNS},
            "status": "FAIL",
            "missing_dimensions": list(DIMENSION_PATTERNS.keys()),
            "feedback": ["No resume text supplied for metric diversity analysis."]
        }

    breakdown: Dict[str, List[str]] = {}
    
    for category, patterns in DIMENSION_PATTERNS.items():
        found = []
        for pat in patterns:
            matches = re.finditer(pat, text, re.IGNORECASE)
            for m in matches:
                span_text = m.group(0).strip()
                if span_text not in found:
                    found.append(span_text)
        breakdown[category] = found

    covered_dimensions = [cat for cat, matches in breakdown.items() if len(matches) > 0]
    covered_count = len(covered_dimensions)
    missing_dimensions = [cat for cat, matches in breakdown.items() if len(matches) == 0]

    # Diversity score (20 points per dimension)
    diversity_score = min(100.0, covered_count * 20.0)

    feedback: List[str] = []
    if covered_count >= 4:
        status = "EXCELLENT"
        feedback.append(f"Outstanding metric breadth ({covered_count}/5 dimensions covered). Resumes with multi-dimensional impact capture leadership attention.")
    elif covered_count >= 3:
        status = "PASS"
        feedback.append(f"Solid metric diversity ({covered_count}/5 dimensions). Consider expanding into: {', '.join(missing_dimensions)}.")
    elif covered_count >= 1:
        status = "WARNING"
        feedback.append(f"Limited metric variety ({covered_count}/5 dimensions). Resume is heavily skewed. Add data covering: {', '.join(missing_dimensions)}.")
    else:
        status = "CRITICAL"
        feedback.append("No quantified metrics detected across any dimensions. Quantified impact (XYZ format) is vital for high ATS ranking.")

    return {
        "diversity_score": diversity_score,
        "dimensions_covered": covered_count,
        "covered_categories": covered_dimensions,
        "missing_dimensions": missing_dimensions,
        "dimension_breakdown": breakdown,
        "status": status,
        "feedback": feedback
    }
