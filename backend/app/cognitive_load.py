"""Cognitive Load & Readability Index Engine.

Computes Gunning Fog Index, Coleman-Liau Index, Automated Readability Index (ARI),
and evaluates the Recruiter 6-Second Glance Skimmability / Cognitive Load Index.
"""

from __future__ import annotations

import re
import math
from typing import Any, Dict, List


def _count_syllables_word(word: str) -> int:
    """Estimates the number of syllables in an English word."""
    clean_word = re.sub(r"[^a-zA-Z]", "", word.lower())
    if not clean_word:
        return 0
    if len(clean_word) <= 3:
        return 1
    # Count vowel groups
    vowel_groups = re.findall(r"[aeiouy]+", clean_word)
    count = len(vowel_groups)
    # Silent trailing 'e'
    if clean_word.endswith("e") and not clean_word.endswith("le") and len(clean_word) > 2:
        if not clean_word.endswith("ee"):
            count -= 1
    # Trailing 'ed' or 'es'
    if clean_word.endswith("ed") or clean_word.endswith("es"):
        if count > 1:
            count -= 1
    return max(1, count)


def evaluate_cognitive_load(text: str) -> Dict[str, Any]:
    """Calculates advanced readability metrics and cognitive load for resume text.

    Formulas:
    - Gunning Fog: 0.4 * ((words / sentences) + 100 * (complex_words / words))
      where complex words have >= 3 syllables.
    - Coleman-Liau: 0.0588 * L - 0.296 * S - 15.8
      where L = (letters / words) * 100, S = (sentences / words) * 100.
    - Automated Readability Index (ARI): 4.71 * (chars / words) + 0.5 * (words / sentences) - 21.43.
    - Recruiter Cognitive Load Score (0-100): High score = low cognitive strain / high skimmability.

    Args:
        text: Raw resume plain text.

    Returns:
        Dict containing indices, cognitive load score, skimmability rating, and recommendations.
    """
    if not text or not text.strip():
        return {
            "gunning_fog_index": 0.0,
            "coleman_liau_index": 0.0,
            "automated_readability_index": 0.0,
            "cognitive_load_score": 0.0,
            "skimmability_rating": "UNEVALUATED",
            "total_words": 0,
            "total_sentences": 0,
            "complex_words_count": 0,
            "avg_sentence_length": 0.0,
            "recommendations": ["No text provided to evaluate readability and cognitive load."],
        }

    # Extract sentences / bullets
    raw_sentences = [s.strip() for s in re.split(r"[.\n;•\-\*\t]+", text) if len(s.strip()) > 3]
    sentences_count = max(1, len(raw_sentences))

    # Extract words
    words = [w for w in re.findall(r"\b[A-Za-z0-9\$\%/\-\.\_]+\b", text) if not w.isnumeric()]
    words_count = max(1, len(words))

    # Character and letter counts
    letters_count = sum(len(re.sub(r"[^A-Za-z]", "", w)) for w in words)
    chars_count = sum(len(w) for w in words)

    # Complex words (>= 3 syllables)
    complex_words_count = 0
    for w in words:
        if _count_syllables_word(w) >= 3:
            complex_words_count += 1

    # 1. Gunning Fog
    pct_complex = (complex_words_count / words_count) * 100.0
    avg_words_per_sentence = words_count / sentences_count
    gunning_fog = 0.4 * (avg_words_per_sentence + pct_complex)

    # 2. Coleman-Liau
    L = (letters_count / words_count) * 100.0
    S = (sentences_count / words_count) * 100.0
    coleman_liau = 0.0588 * L - 0.296 * S - 15.8

    # 3. ARI
    ari = 4.71 * (chars_count / words_count) + 0.5 * avg_words_per_sentence - 21.43

    # Clean & clamp indices
    gunning_fog = max(1.0, min(25.0, round(gunning_fog, 2)))
    coleman_liau = max(1.0, min(25.0, round(coleman_liau, 2)))
    ari = max(1.0, min(25.0, round(ari, 2)))

    # Compute Recruiter Cognitive Load / Skimmability Score (0 - 100)
    # Ideal target: Gunning Fog between 8 and 14 (professional yet easily scanned in 6 seconds)
    fog_deviation = abs(gunning_fog - 11.0)
    fog_penalty = min(40.0, fog_deviation * 5.0)

    # Target sentence length: 12-20 words per bullet
    sentence_len_penalty = (
        0.0 if 10 <= avg_words_per_sentence <= 24 else min(30.0, abs(avg_words_per_sentence - 17.0) * 3.0)
    )

    # Polysyllabic density penalty
    poly_penalty = min(30.0, max(0.0, (pct_complex - 30.0) * 1.5))

    cognitive_score = max(10.0, min(100.0, round(100.0 - (fog_penalty + sentence_len_penalty + poly_penalty), 1)))

    if cognitive_score >= 85.0:
        skimmability = "OPTIMAL_SKIMMABILITY"
    elif cognitive_score >= 70.0:
        skimmability = "GOOD_SKIMMABILITY"
    elif cognitive_score >= 50.0:
        skimmability = "MODERATE_COGNITIVE_STRAIN"
    else:
        skimmability = "HIGH_COGNITIVE_STRAIN"

    recommendations: List[str] = []
    if gunning_fog > 15.0:
        recommendations.append(
            f"High Gunning Fog Index ({gunning_fog}): Simplify overly labyrinthine sentence clauses and prune unnecessary jargon."
        )
    if avg_words_per_sentence > 25.0:
        recommendations.append(
            f"Average bullet length is long ({round(avg_words_per_sentence, 1)} words): Break complex multi-clause bullets into concise action-oriented statements."
        )
    if pct_complex > 35.0:
        recommendations.append(
            f"High polysyllable density ({round(pct_complex, 1)}%): Use crisp, direct action verbs instead of verbose buzzwords."
        )
    if not recommendations:
        recommendations.append(
            "Resume readability is well-calibrated for rapid recruiter review and ATS token parsing."
        )

    return {
        "gunning_fog_index": gunning_fog,
        "coleman_liau_index": coleman_liau,
        "automated_readability_index": ari,
        "cognitive_load_score": cognitive_score,
        "skimmability_rating": skimmability,
        "total_words": words_count,
        "total_sentences": sentences_count,
        "complex_words_count": complex_words_count,
        "avg_sentence_length": round(avg_words_per_sentence, 1),
        "recommendations": recommendations,
    }
