"""
Passive Voice Density & Active Voice Ratio Detector.
Analyzes resume bullet points and sentences to detect passive voice constructions
and recommend authoritative, active-voice impact framing.
"""

import re
from typing import Dict, Any, List

# Common passive markers: auxiliary verbs followed by past participles
PASSIVE_PATTERNS = [
    r'\b(?:was|were|is|are|been|being|be)\s+([a-z]+(?:ed|en|t|wn|ne))\b',
    r'\b(?:was|were)\s+(?:tasked\s+with|responsible\s+for|assigned\s+to|involved\s+in)\b',
    r'\b(?:responsibilities\s+(?:included|were))\b',
    r'\b(?:helped\s+(?:with|to))\b',
    r'\b(?:worked\s+on)\b',
]


def analyze_voice(text: str) -> Dict[str, Any]:
    """
    Evaluates text for passive vs active voice phrasing.
    Optimal ATS standard: <= 10% passive voice density (90%+ active voice).
    """
    if not text or not text.strip():
        return {
            "total_sentences": 0,
            "passive_count": 0,
            "active_count": 0,
            "passive_density_pct": 0.0,
            "active_ratio_pct": 100.0,
            "passive_instances": [],
            "status": "PASS",
            "feedback": ["No text provided for voice analysis."]
        }

    # Split into lines/sentences
    sentences = [s.strip() for s in re.split(r'[\n•\-\*]+|(?<=[.!?])\s+', text) if len(s.strip()) > 5]
    total_sentences = len(sentences)

    if total_sentences == 0:
        return {
            "total_sentences": 0,
            "passive_count": 0,
            "active_count": 0,
            "passive_density_pct": 0.0,
            "active_ratio_pct": 100.0,
            "passive_instances": [],
            "status": "PASS",
            "feedback": ["Insufficient sentence structure detected."]
        }

    passive_instances: List[Dict[str, str]] = []
    
    for sentence in sentences:
        for pattern in PASSIVE_PATTERNS:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                matched_phrase = match.group(0)
                # Formulate suggestion
                suggestion = "Lead with a strong action verb (e.g., 'Engineered', 'Spearheaded', 'Delivered') instead of passive framing."
                if "responsible for" in matched_phrase.lower() or "responsibilities" in matched_phrase.lower():
                    suggestion = "Replace 'Responsible for' with the exact action executed (e.g., 'Directed', 'Orchestrated')."
                elif "tasked with" in matched_phrase.lower() or "assigned to" in matched_phrase.lower():
                    suggestion = "Replace 'Tasked with' by stating your direct leadership and quantifiable achievement."
                elif "helped" in matched_phrase.lower() or "worked on" in matched_phrase.lower():
                    suggestion = "Replace weak collaborator verbs ('helped', 'worked on') with your explicit contribution (e.g., 'Co-authored', 'Accelerated')."

                passive_instances.append({
                    "sentence": sentence,
                    "flagged_phrase": matched_phrase,
                    "recommendation": suggestion
                })
                break  # Count once per sentence

    passive_count = len(passive_instances)
    active_count = max(0, total_sentences - passive_count)
    passive_pct = round((passive_count / total_sentences) * 100.0, 1)
    active_pct = round(100.0 - passive_pct, 1)

    feedback: List[str] = []
    if passive_pct == 0.0:
        status = "EXCELLENT"
        feedback.append("100% active voice. Every bullet point demonstrates direct ownership and impact.")
    elif passive_pct <= 15.0:
        status = "PASS"
        feedback.append(f"Strong active voice profile ({active_pct}% active). Minor passive phrasing detected ({passive_count} instances).")
    elif passive_pct <= 30.0:
        status = "WARNING"
        feedback.append(f"Moderate passive voice density ({passive_pct}%). Convert passive phrases into authoritative action verbs.")
    else:
        status = "CRITICAL"
        feedback.append(f"High passive voice density ({passive_pct}%). Resumes with high passive voice appear hesitant and dilute individual ownership.")

    return {
        "total_sentences": total_sentences,
        "passive_count": passive_count,
        "active_count": active_count,
        "passive_density_pct": passive_pct,
        "active_ratio_pct": active_pct,
        "passive_instances": passive_instances,
        "status": status,
        "feedback": feedback
    }
