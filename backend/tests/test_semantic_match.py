import pytest
from app.semantic_match import (
    compute_jaccard_similarity,
    calculate_semantic_alignment,
    _tokenize,
    _extract_ngrams
)

def test_tokenize_and_ngrams():
    text = "Senior Python Developer with FastAPI and Docker experience"
    tokens = _tokenize(text)
    assert "senior" in tokens
    assert "python" in tokens
    assert "fastapi" in tokens
    assert "with" not in tokens  # stopword removed

    bigrams = _extract_ngrams(tokens, 2)
    assert len(bigrams) == len(tokens) - 1
    assert "senior python" in bigrams

def test_jaccard_similarity_bounds():
    s1 = {"python", "fastapi", "docker"}
    s2 = {"python", "fastapi", "docker"}
    assert compute_jaccard_similarity(s1, s2) == 1.0

    s3 = {"kubernetes", "golang"}
    assert compute_jaccard_similarity(s1, s3) == 0.0

    assert compute_jaccard_similarity(set(), s1) == 0.0

def test_semantic_alignment_empty():
    res = calculate_semantic_alignment("", "Python developer")
    assert res["overall_similarity_score"] == 0.0
    assert res["match_tier"] == "Insufficient Input"

    res_empty_jd = calculate_semantic_alignment("Python developer", "")
    assert res_empty_jd["overall_similarity_score"] == 0.0

def test_semantic_alignment_matching():
    resume = "Senior Python Backend Engineer proficient in FastAPI, PostgreSQL, Docker, and AWS."
    jd = "Seeking Senior Python Engineer with FastAPI, Docker, and PostgreSQL background."

    result = calculate_semantic_alignment(resume, jd)
    assert result["overall_similarity_score"] > 60.0
    assert result["jd_term_coverage_pct"] > 50.0
    assert "python" in result["top_matched_terms"]
    assert result["shared_unigrams_count"] >= 3

def test_semantic_match_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.post("/api/semantic-match", json={
        "resume_text": "Senior Python Backend Engineer proficient in FastAPI, PostgreSQL, Docker, and AWS.",
        "job_description": "Seeking Senior Python Engineer with FastAPI, Docker, and PostgreSQL background."
    })
    assert response.status_code == 200
    data = response.json()
    assert "overall_similarity_score" in data
    assert data["overall_similarity_score"] > 50
    assert "unigram_jaccard" in data

