"""
Resume Bullet Point Typography & Typo Linter.
Audits trailing punctuation consistency, typographical hygiene,
spacing anomalies, and common resume typos across bullet points.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

COMMON_RESUME_TYPOS: Dict[str, str] = {
    "manger": "manager",
    "teh": "the",
    "definately": "definitely",
    "definatly": "definitely",
    "recieve": "receive",
    "recieved": "received",
    "seperate": "separate",
    "seperated": "separated",
    "experiance": "experience",
    "responsibilty": "responsibility",
    "responsabilities": "responsibilities",
    "acheive": "achieve",
    "acheived": "achieved",
    "liason": "liaison",
    "maintainance": "maintenance",
    "occurrance": "occurrence",
    "priviledge": "privilege",
    "sucessful": "successful",
    "sucessfully": "successfully",
    "enviroment": "environment",
    "developement": "development",
    "implemeted": "implemented",
    "performace": "performance",
    "optmized": "optimized",
    "colaberated": "collaborated",
    "intgrated": "integrated"
}

def audit_single_bullet_typography(bullet: str) -> Dict[str, Any]:
    """
    Audits an individual bullet point for typography, punctuation, and typos.
    """
    if not bullet or not bullet.strip():
        return {
            "bullet": bullet,
            "has_issues": False,
            "issues": [],
            "suggested_bullet": bullet,
            "has_trailing_period": False
        }

    raw = bullet.strip()
    # Strip leading bullet symbols if present
    cleaned = re.sub(r"^[\u2022\u2023\u25E6\u2043\u2219\*\-\+]\s*", "", raw)
    issues = []
    fixed = cleaned

    # Check trailing punctuation
    has_trailing_period = cleaned.endswith(".") or cleaned.endswith(";")
    
    # Check double punctuation like '..' or ',,'
    if re.search(r"\.{2,}", cleaned) and not re.search(r"\.\.\.", cleaned):
        issues.append("Double period found ('..')")
        fixed = re.sub(r"\.{2,}", ".", fixed)

    if re.search(r",{2,}", cleaned):
        issues.append("Double comma found (',,')")
        fixed = re.sub(r",{2,}", ",", fixed)

    # Check multiple spaces
    if re.search(r"[^\S\r\n]{2,}", cleaned):
        issues.append("Multiple consecutive spaces detected")
        fixed = re.sub(r"[^\S\r\n]{2,}", " ", fixed)

    # Check missing space after comma
    if re.search(r",[A-Za-z]", cleaned):
        issues.append("Missing space after comma (e.g. 'word,word')")
        fixed = re.sub(r",([A-Za-z])", r", \1", fixed)

    # Check missing space after sentence period (excluding acronyms/urls)
    if re.search(r"\b[a-z]{2,}\.[A-Z]", cleaned):
        issues.append("Missing space after period between sentences")
        fixed = re.sub(r"\b([a-z]{2,})\.([A-Z])", r"\1. \2", fixed)

    # Check unpaired parentheses/brackets
    open_paren = cleaned.count("(")
    close_paren = cleaned.count(")")
    if open_paren != close_paren:
        issues.append(f"Unbalanced parentheses: {open_paren} '(' vs {close_paren} ')'")

    open_bracket = cleaned.count("[")
    close_bracket = cleaned.count("]")
    if open_bracket != close_bracket:
        issues.append(f"Unbalanced brackets: {open_bracket} '[' vs {close_bracket} ']'")

    # Check common typos
    words = re.findall(r"\b[a-zA-Z]+\b", cleaned)
    for word in words:
        lower_word = word.lower()
        if lower_word in COMMON_RESUME_TYPOS:
            correction = COMMON_RESUME_TYPOS[lower_word]
            # Match capitalization
            if word.isupper():
                correction_cased = correction.upper()
            elif word[0].isupper():
                correction_cased = correction.capitalize()
            else:
                correction_cased = correction
            issues.append(f"Potential typo detected: '{word}' -> suggested '{correction_cased}'")
            # Replace full word
            fixed = re.sub(rf"\b{re.escape(word)}\b", correction_cased, fixed)

    return {
        "bullet": raw,
        "has_issues": len(issues) > 0,
        "issues": issues,
        "suggested_bullet": fixed,
        "has_trailing_period": has_trailing_period
    }

def audit_bullet_list_typography(bullets: List[str]) -> Dict[str, Any]:
    """
    Audits a collection of resume bullet points for individual errors
    and list-wide formatting consistency (e.g. period style uniformity).
    """
    if not bullets:
        return {
            "total_bullets": 0,
            "clean_bullets_count": 0,
            "cleanliness_score": 100,
            "period_consistency": "Consistent",
            "period_style": "None",
            "bullets_audit": [],
            "overall_alerts": []
        }

    audits = [audit_single_bullet_typography(b) for b in bullets if b and b.strip()]
    if not audits:
        return {
            "total_bullets": 0,
            "clean_bullets_count": 0,
            "cleanliness_score": 100,
            "period_consistency": "Consistent",
            "period_style": "None",
            "bullets_audit": [],
            "overall_alerts": []
        }

    total = len(audits)
    with_period = sum(1 for a in audits if a["has_trailing_period"])
    without_period = total - with_period

    overall_alerts = []
    # Check consistency of trailing periods
    if with_period > 0 and without_period > 0:
        period_consistency = "Inconsistent"
        overall_alerts.append(
            f"Inconsistent bullet endings: {with_period} bullets end with a period, "
            f"while {without_period} do not. Choose one standard style across all bullets."
        )
        period_style = "Mixed"
    elif with_period == total:
        period_consistency = "Consistent"
        period_style = "All Periods"
    else:
        period_consistency = "Consistent"
        period_style = "No Periods"

    clean_count = sum(1 for a in audits if not a["has_issues"])
    
    # Calculate cleanliness score
    base_cleanliness = (clean_count / total) * 100.0 if total > 0 else 100.0
    if period_consistency == "Inconsistent":
        base_cleanliness = max(base_cleanliness - 15.0, 0.0)

    score = round(base_cleanliness)

    return {
        "total_bullets": total,
        "clean_bullets_count": clean_count,
        "cleanliness_score": score,
        "period_consistency": period_consistency,
        "period_style": period_style,
        "bullets_audit": audits,
        "overall_alerts": overall_alerts
    }
