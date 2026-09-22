"""
Executive Summary vs Outdated Objective Statement Classifier.
Differentiates outdated 1990s candidate-centric 'Career Objectives' from modern,
high-impact 'Professional Summaries / Value Propositions'.
"""

import re
from typing import Dict, Any, List

OBJECTIVE_MARKERS = [
    r'\b(?:seeking|look(?:ing)?\s+for)\s+(?:a|an)?\s*(?:[a-z\-]+\s+)?(?:position|role|opportunity|job)\b',
    r'\b(?:to\s+obtain|to\s+secure)\s+(?:a|an)?\s*(?:[a-z\-]+\s+)?(?:position|role|job|internship)\b',
    r'\bwhere\s+i\s+can\s+(?:utilize|apply|grow|expand)\s+(?:my)?\s*(?:skills|knowledge|talents)\b',
    r'\bfor\s+mutual\s+growth\b',
    r'\bobjective\s*:'
]

VALUE_SUMMARY_MARKERS = [
    r'\b(?:\d+\+?\s+years\s+(?:of\s+)?experience)\b',
    r'\b(?:proven\s+track\s+record|specializing\s+in|demonstrated\s+expertise|adept\s+at)\b',
    r'\b(?:full-stack|backend|frontend|systems|cloud|devops|data|ai|ml|principal|staff|lead|senior)\s+(?:engineer|architect|developer|leader)\b',
    r'\b(?:architected|engineered|spearheaded|delivered)\b'
]


def classify_summary_style(summary_text: str) -> Dict[str, Any]:
    """
    Classifies resume summary into 'MODERN_VALUE_SUMMARY', 'OUTDATED_OBJECTIVE', or 'HYBRID_MIXED'.
    """
    if not summary_text or not summary_text.strip():
        return {
            "style": "MISSING",
            "modernity_score": 0.0,
            "objective_markers_detected": [],
            "value_markers_detected": [],
            "status": "PASS",
            "feedback": ["No professional summary or objective statement provided."]
        }

    text_lower = summary_text.lower()
    
    obj_matches: List[str] = []
    for pat in OBJECTIVE_MARKERS:
        for m in re.finditer(pat, text_lower):
            obj_matches.append(m.group(0))

    val_matches: List[str] = []
    for pat in VALUE_SUMMARY_MARKERS:
        for m in re.finditer(pat, text_lower):
            val_matches.append(m.group(0))

    has_objective = len(obj_matches) > 0
    has_value = len(val_matches) > 0

    feedback: List[str] = []
    
    if has_objective and not has_value:
        style = "OUTDATED_OBJECTIVE"
        score = 25.0
        status = "CRITICAL"
        feedback.append("Outdated 'Career Objective' phrasing detected. Modern hiring managers prefer a Value Proposition summarizing what you bring to the employer rather than what you hope to obtain.")
    elif has_objective and has_value:
        style = "HYBRID_MIXED"
        score = 60.0
        status = "WARNING"
        feedback.append("Summary contains both modern value statements and self-serving objective phrasing. Remove phrases like 'seeking a role' to focus purely on your technical value.")
    elif has_value:
        style = "MODERN_VALUE_SUMMARY"
        score = 100.0
        status = "EXCELLENT"
        feedback.append("Modern Executive Value Summary. Effectively highlights years of expertise, core domain specializations, and proven track record.")
    else:
        style = "GENERIC_SUMMARY"
        score = 70.0
        status = "PASS"
        feedback.append("Summary is neutral. Consider strengthening it with explicit years of experience, primary domain focus, and key architectural achievements.")

    return {
        "style": style,
        "modernity_score": score,
        "objective_markers_detected": list(set(obj_matches)),
        "value_markers_detected": list(set(val_matches)),
        "status": status,
        "feedback": feedback
    }
