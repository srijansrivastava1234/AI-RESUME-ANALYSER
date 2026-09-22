"""
Bullet Point Word Count & Length Distribution Auditor.
Evaluates individual resume bullet points against recruiter visual eye-tracking
and ATS scannability sweet-spots (15-25 words per bullet).
"""

import re
import math
from typing import Dict, Any, List


def analyze_bullet_lengths(text: str) -> Dict[str, Any]:
    """
    Audits the length and word-count distribution of resume bullet points.
    Ideal sweet spot: 15 to 25 words per bullet point.
    """
    if not text or not text.strip():
        return {
            "total_bullets": 0,
            "mean_words_per_bullet": 0.0,
            "optimal_count": 0,
            "optimal_percentage": 0.0,
            "stubs_count": 0,
            "run_on_count": 0,
            "distribution": {"too_short": 0, "brief": 0, "optimal": 0, "long": 0, "run_on": 0},
            "scannability_score": 0.0,
            "status": "PASS",
            "feedback": ["No bullets provided for length analysis."]
        }

    # Extract bullet points (lines starting with -, •, *, numbers, or lines separated by newlines)
    raw_lines = re.split(r'\n+', text)
    bullets = []
    for line in raw_lines:
        cleaned = re.sub(r'^[•\-\*\d\.\)\s]+', '', line).strip()
        if len(cleaned) > 10:  # Valid candidate bullet
            bullets.append(cleaned)

    if not bullets:
        return {
            "total_bullets": 0,
            "mean_words_per_bullet": 0.0,
            "optimal_count": 0,
            "optimal_percentage": 0.0,
            "stubs_count": 0,
            "run_on_count": 0,
            "distribution": {"too_short": 0, "brief": 0, "optimal": 0, "long": 0, "run_on": 0},
            "scannability_score": 50.0,
            "status": "WARNING",
            "feedback": ["No distinct bullet points identified in text."]
        }

    distribution = {
        "too_short": 0,   # < 8 words
        "brief": 0,       # 8-14 words
        "optimal": 0,     # 15-25 words
        "long": 0,        # 26-35 words
        "run_on": 0       # > 35 words
    }

    word_counts = []
    flagged_bullets: List[Dict[str, Any]] = []

    for b in bullets:
        words = re.findall(r'\b[a-zA-Z0-9\-\$\%\.\,\/]+\b', b)
        wc = len(words)
        word_counts.append(wc)

        if wc < 8:
            distribution["too_short"] += 1
            flagged_bullets.append({"bullet": b, "word_count": wc, "issue": "Underdeveloped stub (<8 words). Add context or outcome."})
        elif 8 <= wc <= 14:
            distribution["brief"] += 1
        elif 15 <= wc <= 25:
            distribution["optimal"] += 1
        elif 26 <= wc <= 35:
            distribution["long"] += 1
        else:
            distribution["run_on"] += 1
            flagged_bullets.append({"bullet": b, "word_count": wc, "issue": "Wall of text (>35 words). Break into 2 punchy bullet points."})

    total_bullets = len(bullets)
    mean_wc = round(sum(word_counts) / total_bullets, 1)
    optimal_pct = round((distribution["optimal"] / total_bullets) * 100.0, 1)

    # Scannability score
    # Base: optimal * 1.0 + brief * 0.8 + long * 0.7 + too_short * 0.4 + run_on * 0.3
    weighted = (
        (distribution["optimal"] * 100.0) +
        (distribution["brief"] * 80.0) +
        (distribution["long"] * 70.0) +
        (distribution["too_short"] * 40.0) +
        (distribution["run_on"] * 30.0)
    ) / total_bullets

    scannability_score = max(0.0, min(100.0, round(weighted, 1)))

    feedback: List[str] = []
    if scannability_score >= 80.0:
        status = "EXCELLENT"
        feedback.append(f"Excellent bullet scannability ({optimal_pct}% in the optimal 15-25 word sweet spot).")
    elif scannability_score >= 65.0:
        status = "PASS"
        feedback.append(f"Good bullet lengths (mean {mean_wc} words/bullet).")
    else:
        status = "WARNING"
        feedback.append("Suboptimal bullet length distribution. Several bullets are either too brief stubs or multi-line walls of text.")

    if distribution["run_on"] > 0:
        feedback.append(f"{distribution['run_on']} run-on bullet(s) detected (>35 words). Split dense paragraphs for better 6-second recruiter glanceability.")
    if distribution["too_short"] > 0:
        feedback.append(f"{distribution['too_short']} short bullet(s) detected (<8 words). Expand with quantified results.")

    return {
        "total_bullets": total_bullets,
        "mean_words_per_bullet": mean_wc,
        "optimal_count": distribution["optimal"],
        "optimal_percentage": optimal_pct,
        "stubs_count": distribution["too_short"],
        "run_on_count": distribution["run_on"],
        "distribution": distribution,
        "scannability_score": scannability_score,
        "flagged_bullets": flagged_bullets[:5],  # top 5
        "status": status,
        "feedback": feedback
    }
