"""
Readability & Linguistic Clarity Engine for ATS Resumes.
Calculates Flesch Reading Ease, Flesch-Kincaid Grade Level, and Gunning Fog Index
to assess how easily recruiters and hiring managers can parse executive content.
"""

import re
from typing import Dict, Any, List


def count_syllables(word: str) -> int:
    """Estimates syllable count for a single English word."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1

    # Remove non-alphabetic trailing characters
    word = re.sub(r'[^a-z]', '', word)
    if not word:
        return 0

    # Common end replacements
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    
    syllables = len(re.findall(r'[aeiouy]{1,2}', word))
    return max(1, syllables)


def calculate_readability_metrics(text: str) -> Dict[str, Any]:
    """
    Analyzes text and returns comprehensive readability diagnostics.
    Optimal recruiter reading grade level for resumes is typically Grade 8 - 12.
    """
    if not text or not text.strip():
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "gunning_fog_index": 0.0,
            "word_count": 0,
            "sentence_count": 0,
            "avg_words_per_sentence": 0.0,
            "complex_word_count": 0,
            "complex_word_percentage": 0.0,
            "readability_tier": "Insufficient Text",
            "is_optimal": False,
            "feedback": ["Resume text is empty or contains insufficient content for readability analysis."]
        }

    # Extract sentences (handling newlines, bullet points, periods, exclamation, questions)
    raw_sentences = [s.strip() for s in re.split(r'[\n.!?]+', text) if s.strip()]
    sentence_count = max(1, len(raw_sentences))

    # Extract words
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    word_count = len(words)

    if word_count < 5:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "gunning_fog_index": 0.0,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": round(word_count / sentence_count, 1),
            "complex_word_count": 0,
            "complex_word_percentage": 0.0,
            "readability_tier": "Insufficient Words",
            "is_optimal": False,
            "feedback": ["Resume content is too short for meaningful readability evaluation."]
        }

    syllable_counts = [count_syllables(w) for w in words]
    total_syllables = sum(syllable_counts)
    complex_words = [w for w, count in zip(words, syllable_counts) if count >= 3]
    complex_word_count = len(complex_words)

    words_per_sentence = word_count / sentence_count
    syllables_per_word = total_syllables / word_count
    complex_word_pct = (complex_word_count / word_count) * 100.0

    # 1. Flesch Reading Ease: 206.835 - 1.015 * (words/sentence) - 84.6 * (syllables/word)
    fre = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
    fre = max(0.0, min(100.0, fre))

    # 2. Flesch-Kincaid Grade Level: 0.39 * (words/sentence) + 11.8 * (syllables/word) - 15.59
    fkgl = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59
    fkgl = max(0.0, fkgl)

    # 3. Gunning Fog Index: 0.4 * ((words/sentence) + complex_word_pct)
    fog = 0.4 * (words_per_sentence + complex_word_pct)
    fog = max(0.0, fog)

    # Classification & Feedback
    feedback: List[str] = []
    if 8.0 <= fkgl <= 12.5:
        tier = "Optimal Executive Readability"
        is_optimal = True
        feedback.append("Resume reading grade level is optimal (Grade 8-12), ensuring rapid recruiter comprehension.")
    elif fkgl < 8.0:
        tier = "Overly Simplistic / Low Information Density"
        is_optimal = False
        feedback.append("Text readability is below Grade 8. Consider incorporating stronger technical vocabulary and detailed metric scope.")
    else:
        tier = "Dense / High Syntactic Complexity"
        is_optimal = False
        feedback.append("Text reading level exceeds Grade 13. Sentences may be too long or convoluted. Split dense bullet points.")

    if words_per_sentence > 25.0:
        feedback.append(f"Average sentence length ({round(words_per_sentence, 1)} words) is high. Break run-on sentences into punchy action points.")

    if complex_word_pct > 30.0:
        feedback.append(f"High complex word ratio ({round(complex_word_pct, 1)}%). Ensure specialized jargon is balanced with clear action outcomes.")

    return {
        "flesch_reading_ease": round(fre, 1),
        "flesch_kincaid_grade": round(fkgl, 1),
        "gunning_fog_index": round(fog, 1),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_words_per_sentence": round(words_per_sentence, 1),
        "complex_word_count": complex_word_count,
        "complex_word_percentage": round(complex_word_pct, 1),
        "readability_tier": tier,
        "is_optimal": is_optimal,
        "feedback": feedback
    }
