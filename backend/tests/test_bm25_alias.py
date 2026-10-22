"""
Unit tests for the bm25 backward-compatibility alias module.
Verifies that all re-exported symbols, functions, and scoring constants
remain 100% synchronized with app.bm25_scorer.
"""

import pytest
import app.bm25 as bm25_alias
import app.bm25_scorer as bm25_source


def test_bm25_all_exports_match():
    assert set(bm25_alias.__all__) == {
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
    }
    for symbol in bm25_alias.__all__:
        assert hasattr(bm25_alias, symbol), f"Missing symbol {symbol} in app.bm25"
        if symbol == "calculate_bm25_score":
            assert getattr(bm25_alias, symbol) is bm25_source.compute_bm25_plus
        else:
            assert getattr(bm25_alias, symbol) is getattr(bm25_source, symbol)


def test_bm25_alias_tokenization():
    text = "Architected high-throughput microservices using Python & Go!"
    tokens = bm25_alias.tokenize(text)
    assert "architected" in tokens
    assert "high-throughput" in tokens or "throughput" in tokens
    assert "microservices" in tokens
    assert "python" in tokens
    assert "go" in tokens


def test_bm25_alias_idf_calculation():
    idf_default = bm25_alias.calculate_idf("kubernetes")
    idf_custom = bm25_alias.calculate_idf("python", corpus_size=500, doc_freq=50)
    assert isinstance(idf_default, float)
    assert isinstance(idf_custom, float)
    assert idf_default > 0.0
    assert idf_custom > 0.0


def test_bm25_alias_scoring():
    resume_text = "Senior Python engineer building FastAPI microservices and Docker containers."
    keywords = ["python", "fastapi", "docker", "kubernetes"]

    score_result_1 = bm25_alias.compute_bm25_plus(resume_text, keywords)
    score_result_2 = bm25_alias.calculate_bm25_score(resume_text, keywords)

    assert score_result_1 == score_result_2
    assert score_result_1["normalized_score"] > 0
    assert score_result_1["matched_keywords"] == 3
    assert score_result_1["total_keywords"] == 4
    assert len(score_result_1["term_breakdown"]) == 4
