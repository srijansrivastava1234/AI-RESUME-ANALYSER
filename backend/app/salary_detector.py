"""
Confidential Salary & Compensation Disclosure Detector.
Scans resumes for inadvertent disclosures of personal salary history, current CTC/LPA,
hourly wage expectations, or compensation demands that weaken negotiation posture.
"""

import re
from typing import Dict, Any, List

PERSONAL_SALARY_PATTERNS = [
    r'\b(?:current|expected|previous|desired|target)\s+(?:salary|ctc|compensation|remuneration|pay|rate|package)\s*(?::|-|=|is)?\s*[\$\€\£\₹]?\s*\d+(?:[,\.]\d+)?\s*(?:k|lpa|k\s*usd|usd|inr|\/hr|\/yr|\/year|\/month|per\s+annum)?\b',
    r'\b(?:ctc|lpa)\s*:\s*[\$\₹]?\s*\d+(?:\.\d+)?\s*(?:lpa|lakhs|k)?\b',
    r'\b(?:salary|hourly\s+rate|earning|making)\s*(?:expectation|demand|requirement)?\s*(?:of|:)?\s*[\$\€\£\₹]\s*\d+(?:[,\.]\d+)?(?:\s*(?:k|\/hr|\/hour|per\s+hour|\/year|\/yr))?\b',
    r'\b[\$\€\£\₹]\s*\d{2,3}(?:,\d{3})*\s*(?:\/hr|per\s+hour|\/year|per\s+year)\b'
]


def detect_salary_disclosures(text: str) -> Dict[str, Any]:
    """
    Detects personal salary disclosures in resume text.
    Resumes should never list current compensation or target wages directly in document text.
    """
    if not text or not text.strip():
        return {
            "has_salary_disclosure": False,
            "disclosures_count": 0,
            "flagged_instances": [],
            "status": "PASS",
            "feedback": ["No text provided for salary audit."]
        }

    disclosures: List[str] = []
    
    for pat in PERSONAL_SALARY_PATTERNS:
        matches = re.finditer(pat, text, re.IGNORECASE)
        for m in matches:
            matched_str = m.group(0).strip()
            if matched_str not in disclosures:
                disclosures.append(matched_str)

    has_disclosure = len(disclosures) > 0
    feedback: List[str] = []

    if has_disclosure:
        status = "CRITICAL"
        feedback.append(
            f"Explicit compensation disclosure detected ({len(disclosures)} instance(s): {', '.join(disclosures)}). "
            "Remove all salary requirements or current earnings from your resume. "
            "Disclosing numbers anchors salary negotiations prematurely and breaches standard NDA / professional etiquette."
        )
    else:
        status = "EXCELLENT"
        feedback.append("No confidential salary or compensation figures detected. Clean privacy posture.")

    return {
        "has_salary_disclosure": has_disclosure,
        "disclosures_count": len(disclosures),
        "flagged_instances": disclosures,
        "status": status,
        "feedback": feedback
    }
