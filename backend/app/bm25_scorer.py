"""
BM25+ Lexical Retrieval & Term Saturation Engine
Implements the Okapi BM25+ information retrieval algorithm (Lv & Zhai, 2011)
calibrated for ATS resume screening and job description keyword ranking.

Formula:
    BM25+(D, Q) = sum_{q in Q} IDF(q) * [ (f(q, D) * (k1 + 1)) / (f(q, D) + k1 * (1 - b + b * (|D| / avgdl))) + delta ]

Where:
    - k1 = 1.2 (term frequency saturation control)
    - b = 0.75 (document length normalization penalty)
    - delta = 1.0 (BM25+ floor parameter preventing penalty on long documents with single matches)
    - avgdl = 450 (empirical average token count for a calibrated 1-2 page professional resume)
"""

import math
import re
from typing import Dict, List, Any, Optional

DEFAULT_K1: float = 1.2
DEFAULT_B: float = 0.75
DEFAULT_DELTA: float = 1.0
DEFAULT_AVGDL: int = 450
KEYWORD_STUFFING_THRESHOLD: int = 6

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "itself", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "she", "should", "so", "some", "such", "than", "that",
    "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


def tokenize(text: str) -> List[str]:
    """Tokenize raw text into lowercase alphanumeric tokens excluding common stopwords."""
    if not text:
        return []
    raw_tokens = re.findall(r"\b[a-zA-Z0-9_\-\.\+#]{2,}\b", text.lower())
    return [t for t in raw_tokens if t not in STOPWORDS]


def calculate_idf(term: str, corpus_size: int = 1000, doc_freq: Optional[int] = None) -> float:
    """
    Calculate Robertson-Spärck Jones Inverse Document Frequency (IDF).
    Formula: IDF(q) = ln( (N - n(q) + 0.5) / (n(q) + 0.5) + 1 )
    """
    if doc_freq is None:
        # Calibrated default: tech keywords appear in ~12% of baseline resumes
        doc_freq = max(1, int(corpus_size * 0.12))
    n_q = max(1, min(corpus_size - 1, doc_freq))
    idf = math.log(((corpus_size - n_q + 0.5) / (n_q + 0.5)) + 1.0)
    return round(idf, 4)


def compute_bm25_plus(
    resume_text: str,
    target_keywords: List[str],
    k1: float = DEFAULT_K1,
    b: float = DEFAULT_B,
    delta: float = DEFAULT_DELTA,
    avgdl: int = DEFAULT_AVGDL,
) -> Dict[str, Any]:
    """
    Calculate BM25+ relevance score for a resume against target job keywords.

    Returns:
        Dict containing:
        - raw_bm25_score: Unbounded BM25+ sum
        - normalized_score: 0-100 normalized ATS relevance index
        - doc_length: Token count of resume
        - length_ratio: Ratio of document length to avgdl
        - keyword_coverage: Percentage of query keywords matched
        - matched_keywords: Count of matched keywords
        - total_keywords: Count of queried keywords
        - term_breakdown: Granular per-term frequency, saturation, and BM25 contribution
        - warnings: Alerts for keyword stuffing, length anomalies, or low coverage
    """
    tokens = tokenize(resume_text)
    doc_len = len(tokens)
    clean_keywords = [k.strip().lower() for k in target_keywords if k and k.strip()]
    unique_keywords = list(dict.fromkeys(clean_keywords))

    if not unique_keywords:
        return {
            "raw_bm25_score": 0.0,
            "normalized_score": 0.0,
            "doc_length": doc_len,
            "length_ratio": round(doc_len / max(1, avgdl), 2) if doc_len else 0.0,
            "keyword_coverage": 0.0,
            "matched_keywords": 0,
            "total_keywords": 0,
            "term_breakdown": [],
            "stuffed_terms": [],
            "warnings": ["No target keywords provided for BM25+ evaluation."]
        }

    if doc_len == 0:
        return {
            "raw_bm25_score": 0.0,
            "normalized_score": 0.0,
            "doc_length": 0,
            "length_ratio": 0.0,
            "keyword_coverage": 0.0,
            "matched_keywords": 0,
            "total_keywords": len(unique_keywords),
            "term_breakdown": [
                {
                    "term": kw,
                    "frequency": 0,
                    "saturation": 0.0,
                    "bm25_contribution": 0.0,
                    "is_stuffed": False
                } for kw in unique_keywords
            ],
            "stuffed_terms": [],
            "warnings": ["Resume contains zero extractable text tokens."]
        }

    # Count term frequencies
    term_counts: Dict[str, int] = {}
    resume_lower = resume_text.lower()
    for kw in unique_keywords:
        # Multi-word keyword phrase search vs single token search
        if " " in kw:
            pattern = r"\b" + re.escape(kw) + r"\b"
            term_counts[kw] = len(re.findall(pattern, resume_lower))
        else:
            term_counts[kw] = tokens.count(kw)

    len_norm = 1.0 - b + (b * (doc_len / avgdl))
    raw_bm25_total = 0.0
    max_theoretical_score = 0.0
    term_breakdown: List[Dict[str, Any]] = []
    stuffed_terms: List[str] = []
    warnings: List[str] = []

    for kw in unique_keywords:
        f_q = term_counts.get(kw, 0)
        idf_q = calculate_idf(kw)
        
        # Max theoretical score assumes ideal non-stuffed frequency (f_q=2) on optimal length doc
        ideal_saturation = (2.0 * (k1 + 1.0)) / (2.0 + k1)
        max_theoretical_score += idf_q * (ideal_saturation + delta)

        if f_q > 0:
            saturation_factor = (f_q * (k1 + 1.0)) / (f_q + (k1 * len_norm))
            term_score = idf_q * (saturation_factor + delta)
            raw_bm25_total += term_score
            saturation_pct = round((saturation_factor / (k1 + 1.0)) * 100, 1)

            is_stuffed = f_q >= KEYWORD_STUFFING_THRESHOLD
            if is_stuffed:
                stuffed_terms.append(kw)

            term_breakdown.append({
                "term": kw,
                "frequency": f_q,
                "saturation": saturation_pct,
                "bm25_contribution": round(term_score, 3),
                "is_stuffed": is_stuffed
            })
        else:
            term_breakdown.append({
                "term": kw,
                "frequency": 0,
                "saturation": 0.0,
                "bm25_contribution": 0.0,
                "is_stuffed": False
            })

    matched_count = sum(1 for t in term_breakdown if t["frequency"] > 0)
    coverage = round((matched_count / len(unique_keywords)) * 100, 1)

    # Normalize to 0-100 scale
    if max_theoretical_score > 0:
        coverage_weight = 0.40
        relevance_weight = 0.60
        normalized_relevance = min(100.0, (raw_bm25_total / max_theoretical_score) * 100.0)
        final_normalized = round((coverage * coverage_weight) + (normalized_relevance * relevance_weight), 1)
    else:
        final_normalized = 0.0

    # Diagnostics & Warnings
    if stuffed_terms:
        warnings.append(
            f"Term frequency saturation detected on: {', '.join(stuffed_terms)}. "
            f"Repeating terms >= {KEYWORD_STUFFING_THRESHOLD} times yields diminishing returns in modern ATS parsers."
        )

    if doc_len > avgdl * 1.8:
        warnings.append(
            f"Document length ({doc_len} tokens) significantly exceeds standard 1-2 page target ({avgdl} tokens). "
            f"BM25+ length normalization penalty applied."
        )
    elif doc_len < avgdl * 0.4:
        warnings.append(
            f"Document length ({doc_len} tokens) is unusually brief. Add verified technical accomplishments to maximize BM25+ recall."
        )

    if coverage < 50.0:
        warnings.append(
            f"Keyword coverage is {coverage}%. Missing {len(unique_keywords) - matched_count} required target skills."
        )

    return {
        "raw_bm25_score": round(raw_bm25_total, 3),
        "normalized_score": min(100.0, max(0.0, final_normalized)),
        "doc_length": doc_len,
        "length_ratio": round(doc_len / max(1, avgdl), 2),
        "keyword_coverage": coverage,
        "matched_keywords": matched_count,
        "total_keywords": len(unique_keywords),
        "term_breakdown": term_breakdown,
        "stuffed_terms": stuffed_terms,
        "warnings": warnings
    }
