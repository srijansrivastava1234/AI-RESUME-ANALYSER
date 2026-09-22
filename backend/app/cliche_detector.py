"""
Weak Filler Word & Corporate Cliché Detector.
Identifies overused resume fluff, generic buzzwords, and unsubstantiated corporate clichés,
providing high-impact, quantifiable alternatives.
"""

import re
from typing import Dict, Any, List

CLICHE_CATALOG: Dict[str, str] = {
    "team player": "Cross-functional Collaborator / Squad Lead",
    "hardworking": "High-Output / Dedicated Producer",
    "go-getter": "Proactive Initiator / Self-Directed Contributor",
    "results-oriented": "Outcome-Driven / KPI-Focused",
    "results driven": "Outcome-Driven / Metric-Focused",
    "detail-oriented": "Precision-Focused / Quality Assurance Lead",
    "detail oriented": "Precision-Focused / Rigorous",
    "self-motivated": "Autonomous / Self-Directed Initiator",
    "self motivated": "Autonomous / Initiative-Driven",
    "think outside the box": "Innovative Problem Solver / Creative Strategist",
    "outside the box": "Innovative / Novel Architectural Approach",
    "synergy": "Cross-System Integration / Operational Alignment",
    "rockstar": "Domain Specialist / Principal Engineer",
    "ninja": "High-Efficiency Engineer / Core Contributor",
    "guru": "Subject Matter Expert / Technical Authority",
    "thought leader": "Domain Innovator / Conference Speaker",
    "passionate": "Committed / Actively Contributing",
    "strategic thinker": "Systems Architect / Long-Term Planner",
    "dynamic personality": "High-Adaptability / Fast-Paced Operator",
    "wearer of many hats": "Multi-Disciplinary Contributor / Full-Stack Generalist",
    "bottom line": "EBITDA / Net Operational Margin",
    "hit the ground running": "Rapid Onboarding / Immediate Contributor",
    "fast learner": "High Technical Velocity / Rapid Skill Acquisition"
}


def audit_cliches(text: str) -> Dict[str, Any]:
    """
    Scans text for corporate clichés and buzzwords, computing cliché penalty and suggestions.
    """
    if not text or not text.strip():
        return {
            "cliche_count": 0,
            "unique_cliches": 0,
            "detected_cliches": [],
            "cleanliness_score": 100.0,
            "status": "PASS",
            "feedback": ["No text provided for cliché audit."]
        }

    detected: List[Dict[str, Any]] = []
    text_lower = text.lower()
    words = re.findall(r'\b[a-zA-Z\-]+\b', text)
    total_words = max(1, len(words))

    for phrase, alternative in CLICHE_CATALOG.items():
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = list(re.finditer(pattern, text_lower))
        if matches:
            detected.append({
                "phrase": phrase,
                "occurrences": len(matches),
                "alternative": alternative,
                "rationale": f"Replace generic cliché '{phrase}' with '{alternative}' or back it up with quantifiable data."
            })

    total_occurrences = sum(item["occurrences"] for item in detected)
    unique_count = len(detected)

    # Cleanliness score out of 100
    penalty = total_occurrences * 8.0
    cleanliness = max(0.0, round(100.0 - penalty, 1))

    feedback: List[str] = []
    if total_occurrences == 0:
        status = "EXCELLENT"
        feedback.append("Zero corporate clichés detected. Resume demonstrates strong professional specificity.")
    elif total_occurrences <= 2:
        status = "PASS"
        feedback.append(f"Minor cliché presence ({total_occurrences} detected). Replace vague buzzwords with concrete achievements.")
    elif total_occurrences <= 4:
        status = "WARNING"
        feedback.append(f"Noticeable buzzword density ({total_occurrences} detected). Recruiters often skip over unsubstantiated claims like 'team player' or 'fast learner'.")
    else:
        status = "CRITICAL"
        feedback.append(f"High buzzword saturation ({total_occurrences} clichés found). Substantially rewrite bullets to emphasize metrics over generic corporate adjectives.")

    return {
        "cliche_count": total_occurrences,
        "unique_cliches": unique_count,
        "detected_cliches": detected,
        "cleanliness_score": cleanliness,
        "status": status,
        "feedback": feedback
    }
