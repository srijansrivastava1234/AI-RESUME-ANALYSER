"""
Unit test suite for BM25+ lexical ranking and term saturation engine.
"""

import pytest
from app.bm25_scorer import (
    tokenize,
    calculate_idf,
    compute_bm25_plus,
    DEFAULT_AVGDL,
    KEYWORD_STUFFING_THRESHOLD,
)


def test_tokenize_empty_and_stopwords():
    assert tokenize("") == []
    tokens = tokenize("The quick brown fox jumps over the lazy dog and a few cats")
    assert "the" not in tokens
    assert "and" not in tokens
    assert "quick" in tokens
    assert "brown" in tokens
    assert "fox" in tokens


def test_calculate_idf():
    idf = calculate_idf("python", corpus_size=1000, doc_freq=120)
    assert idf > 1.5
    # Rarer terms should have higher IDF
    idf_rare = calculate_idf("kubernetes", corpus_size=1000, doc_freq=10)
    idf_common = calculate_idf("communication", corpus_size=1000, doc_freq=500)
    assert idf_rare > idf_common


def test_compute_bm25_plus_empty_inputs():
    res_empty_kw = compute_bm25_plus("Software engineer with Python experience", [])
    assert res_empty_kw["raw_bm25_score"] == 0.0
    assert res_empty_kw["normalized_score"] == 0.0
    assert len(res_empty_kw["warnings"]) > 0

    res_empty_doc = compute_bm25_plus("", ["python", "docker"])
    assert res_empty_doc["raw_bm25_score"] == 0.0
    assert res_empty_doc["doc_length"] == 0
    assert res_empty_doc["keyword_coverage"] == 0.0


def test_compute_bm25_plus_exact_match():
    resume = (
        "Senior Backend Engineer with extensive experience in Python, FastAPI, Docker, "
        "and PostgreSQL. Architected microservices and deployed Kubernetes clusters."
    )
    keywords = ["Python", "FastAPI", "Docker", "PostgreSQL", "Kubernetes"]
    result = compute_bm25_plus(resume, keywords)

    assert result["keyword_coverage"] == 100.0
    assert result["matched_keywords"] == 5
    assert result["normalized_score"] >= 70.0
    assert len(result["stuffed_terms"]) == 0


def test_term_saturation_and_stuffing():
    # Artificially repeat "Python" 10 times (keyword stuffing)
    stuffed_resume = "Python " * 10 + "FastAPI Docker Kubernetes PostgreSQL AWS"
    result = compute_bm25_plus(stuffed_resume, ["Python", "FastAPI", "Docker"])

    assert "python" in [t.lower() for t in result["stuffed_terms"]]
    assert any("saturation detected" in w.lower() for w in result["warnings"])
    
    # Verify saturation is bounded
    term_info = next(t for t in result["term_breakdown"] if t["term"] == "python")
    assert term_info["frequency"] == 10
    assert term_info["is_stuffed"] is True
    assert term_info["saturation"] > 80.0


def test_document_length_normalization():
    short_resume = "Python developer building microservices using Docker and PostgreSQL."
    # Bloated resume with 1200 filler words
    filler = " " .join(["project task implementation review workflow"] * 240)
    long_resume = f"{short_resume} {filler}"

    res_short = compute_bm25_plus(short_resume, ["Python", "Docker"])
    res_long = compute_bm25_plus(long_resume, ["Python", "Docker"])

    # Due to length normalization penalty, matching terms on bloated doc have lower term score
    short_term_score = sum(t["bm25_contribution"] for t in res_short["term_breakdown"])
    long_term_score = sum(t["bm25_contribution"] for t in res_long["term_breakdown"])
    assert short_term_score > long_term_score
    assert any("exceeds standard" in w.lower() for w in res_long["warnings"])


def test_multiword_phrase_matching():
    resume = "Specialized in Machine Learning, Natural Language Processing, and Cloud Computing architecture."
    keywords = ["machine learning", "cloud computing", "kubernetes"]
    result = compute_bm25_plus(resume, keywords)

    assert result["matched_keywords"] == 2
    assert result["keyword_coverage"] == pytest.approx(66.7, abs=0.1)
    ml_term = next(t for t in result["term_breakdown"] if t["term"] == "machine learning")
    assert ml_term["frequency"] >= 1


def test_delta_floor_guarantee():
    # In BM25+, delta parameter guarantees that even when length penalty is severe,
    # a document containing the query term receives a non-trivial floor contribution.
    doc = "Python " + ("word " * 1000)
    res_delta_1 = compute_bm25_plus(doc, ["Python"], delta=1.0)
    res_delta_0 = compute_bm25_plus(doc, ["Python"], delta=0.0)

    assert res_delta_1["raw_bm25_score"] > res_delta_0["raw_bm25_score"]
