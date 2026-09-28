"""
Backward-compatibility alias for bm25_scorer.
"""
from app.bm25_scorer import (
    tokenize,
    calculate_idf,
    compute_bm25_plus,
    compute_bm25_plus as calculate_bm25_score,
    DEFAULT_AVGDL,
    DEFAULT_B,
    DEFAULT_DELTA,
    DEFAULT_K1,
    KEYWORD_STUFFING_THRESHOLD,
    STOPWORDS,
)

__all__ = [
    "tokenize",
    "calculate_idf",
    "compute_bm25_plus",
    "calculate_bm25_score",
    "DEFAULT_AVGDL",
    "DEFAULT_B",
    "DEFAULT_DELTA",
    "DEFAULT_K1",
    "KEYWORD_STUFFING_THRESHOLD",
    "STOPWORDS",
]
