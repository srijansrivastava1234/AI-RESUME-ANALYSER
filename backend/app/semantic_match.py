"""
Semantic Match Scorer using token n-gram Jaccard overlap, weighted term frequencies,
and semantic alignment estimation for resume vs job description matching.
"""

import re
import math
from typing import Dict, Any, List, Set, Tuple
from collections import Counter

STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

def _tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric words."""
    if not text:
        return []
    tokens = re.findall(r"\b[a-zA-Z0-9_+#.-]+\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

def _extract_ngrams(tokens: List[str], n: int) -> List[str]:
    """Extracts contiguous n-grams from a list of tokens."""
    if len(tokens) < n or n < 1:
        return []
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def compute_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Computes Jaccard index between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return round(intersection / union, 4) if union > 0 else 0.0

def calculate_semantic_alignment(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Evaluates semantic similarity between resume and job description using
    unigram and bigram Jaccard similarity, term recall, and coverage metrics.
    """
    if not resume_text or not resume_text.strip() or not jd_text or not jd_text.strip():
        return {
            "overall_similarity_score": 0.0,
            "match_tier": "Insufficient Input",
            "unigram_jaccard": 0.0,
            "bigram_jaccard": 0.0,
            "jd_term_coverage_pct": 0.0,
            "shared_unigrams_count": 0,
            "shared_bigrams_count": 0,
            "top_missing_jd_terms": [],
            "top_matched_terms": [],
            "recommendation": "Provide both resume text and job description to evaluate semantic overlap."
        }

    resume_tokens = _tokenize(resume_text)
    jd_tokens = _tokenize(jd_text)

    resume_unigrams = set(resume_tokens)
    jd_unigrams = set(jd_tokens)

    resume_bigrams = set(_extract_ngrams(resume_tokens, 2))
    jd_bigrams = set(_extract_ngrams(jd_tokens, 2))

    unigram_jaccard = compute_jaccard_similarity(resume_unigrams, jd_unigrams)
    bigram_jaccard = compute_jaccard_similarity(resume_bigrams, jd_bigrams)

    # Calculate JD coverage (what percentage of JD unique keywords are present in resume)
    shared_unigrams = resume_unigrams & jd_unigrams
    shared_bigrams = resume_bigrams & jd_bigrams

    jd_term_coverage = (len(shared_unigrams) / len(jd_unigrams)) if jd_unigrams else 0.0
    jd_coverage_pct = round(jd_term_coverage * 100, 1)

    # Frequency analysis for missing terms in JD
    jd_counts = Counter(jd_tokens)
    missing_terms = [
        term for term, _ in jd_counts.most_common()
        if term not in resume_unigrams
    ][:15]

    matched_terms = [
        term for term, _ in jd_counts.most_common()
        if term in shared_unigrams
    ][:15]

    # Composite similarity score (0 - 100)
    # 50% JD keyword coverage + 30% unigram Jaccard + 20% bigram Jaccard
    composite_raw = (jd_term_coverage * 50.0) + (min(unigram_jaccard * 2.5, 1.0) * 30.0) + (min(bigram_jaccard * 3.5, 1.0) * 20.0)
    composite_score = round(min(max(composite_raw, 0.0), 100.0), 1)

    if composite_score >= 80.0:
        tier = "Excellent Semantic Alignment"
        rec = "Strong semantic and vocabulary overlap with target JD. Ready for submission."
    elif composite_score >= 60.0:
        tier = "Good Alignment (Minor Gaps)"
        rec = f"Good vocabulary overlap. Consider incorporating high-priority missing terms: {', '.join(missing_terms[:5])}."
    elif composite_score >= 40.0:
        tier = "Moderate Alignment"
        rec = f"Moderate match. Incorporate key terminology: {', '.join(missing_terms[:8])}."
    else:
        tier = "Low Semantic Alignment"
        rec = "Significant vocabulary mismatch with job description. Tailor technical keywords and responsibilities."

    return {
        "overall_similarity_score": composite_score,
        "match_tier": tier,
        "unigram_jaccard": unigram_jaccard,
        "bigram_jaccard": bigram_jaccard,
        "jd_term_coverage_pct": jd_coverage_pct,
        "shared_unigrams_count": len(shared_unigrams),
        "shared_bigrams_count": len(shared_bigrams),
        "top_missing_jd_terms": missing_terms,
        "top_matched_terms": matched_terms,
        "recommendation": rec
    }
