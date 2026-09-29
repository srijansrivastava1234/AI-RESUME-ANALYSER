"""
Module: readability_metrics.py
Purpose: Evaluates text complexity using Coleman-Liau Index, Automated Readability Index (ARI),
and executive scannability metrics calibrated for technical hiring managers.
"""

import re
from typing import Dict, Any


def calculate_coleman_liau_index(text: str) -> float:
    """
    Computes the Coleman-Liau Index:
    CLI = 0.0588 * L - 0.296 * S - 15.8
    where L = avg number of letters per 100 words, S = avg number of sentences per 100 words.
    """
    words = [w for w in re.findall(r'\b[a-zA-Z0-9]+\b', text) if w]
    if not words:
        return 0.0

    num_words = len(words)
    num_letters = sum(len(w) for w in words)
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    num_sentences = max(1, len(sentences))

    l_val = (num_letters / num_words) * 100.0
    s_val = (num_sentences / num_words) * 100.0

    cli = 0.0588 * l_val - 0.296 * s_val - 15.8
    return round(max(0.0, cli), 2)


def calculate_automated_readability_index(text: str) -> float:
    """
    Computes Automated Readability Index (ARI):
    ARI = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
    """
    words = [w for w in re.findall(r'\b[a-zA-Z0-9]+\b', text) if w]
    if not words:
        return 0.0

    num_words = len(words)
    num_chars = sum(len(w) for w in words)
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    num_sentences = max(1, len(sentences))

    ari = 4.71 * (num_chars / num_words) + 0.5 * (num_words / num_sentences) - 21.43
    return round(max(0.0, ari), 2)


def evaluate_executive_scannability(text: str) -> Dict[str, Any]:
    """
    Comprehensive executive scannability assessment.
    Target technical resume reading level: Grade 10 - 14 (College level, concise).
    """
    cli = calculate_coleman_liau_index(text)
    ari = calculate_automated_readability_index(text)
    composite_grade = round((cli + ari) / 2.0, 1)

    if 10.0 <= composite_grade <= 15.0:
        verdict = "Optimal Technical Executive Level"
        score = 95
    elif composite_grade < 10.0:
        verdict = "Slightly Simplistic Phrasing"
        score = 80
    else:
        verdict = "Dense / Overly Convoluted Syntax"
        score = 65

    return {
        "coleman_liau_index": cli,
        "automated_readability_index": ari,
        "composite_grade_level": composite_grade,
        "scannability_score": score,
        "verdict": verdict
    }
