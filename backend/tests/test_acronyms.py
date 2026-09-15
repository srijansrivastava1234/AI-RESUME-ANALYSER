import pytest
from app.acronyms import (
    get_canonical_term,
    get_all_aliases,
    expand_technical_terms,
    calculate_synonym_aware_overlap
)
from app.keywords import calculate_keyword_match_score


def test_get_canonical_term():
    assert get_canonical_term("k8s") == "Kubernetes"
    assert get_canonical_term("aws") == "Amazon Web Services"
    assert get_canonical_term("ts") == "TypeScript"
    assert get_canonical_term("psql") == "PostgreSQL"
    assert get_canonical_term("cicd") == "Continuous Integration / Continuous Deployment"
    assert get_canonical_term("unknown_term") == "Unknown_Term"
    assert get_canonical_term("") == ""


def test_get_all_aliases():
    aliases = get_all_aliases("Kubernetes")
    assert "k8s" in aliases
    assert "kubernetes" in aliases


def test_expand_technical_terms():
    sample = "Architected scalable microservices using K8s, AWS, TypeScript, and MongoDB."
    expanded = expand_technical_terms(sample)
    detected = expanded["detected_terms"]
    assert "K8S" in detected or "K8s" in detected
    assert "AWS" in detected
    assert len(expanded["expansions"]) > 0

    # Avoid false positive matching of short acronyms
    html_sample = "Expert in HTML, CSS, and web formatting."
    html_expanded = expand_technical_terms(html_sample)
    # 'ML' should NOT be detected inside 'HTML'
    assert "ML" not in html_expanded["detected_terms"]


def test_calculate_synonym_aware_overlap_matches():
    resume_skills = {"k8s", "ts", "postgres", "fastapi"}
    job_skills = {"kubernetes", "typescript", "postgresql", "fastapi"}

    result = calculate_synonym_aware_overlap(resume_skills, job_skills)
    assert result["match_percentage"] == 100
    assert len(result["missing_skills"]) == 0
    assert len(result["synonym_matches"]) == 3
    # Check that FastAPI was an exact match
    assert any("Fastapi" in s or "FastAPI" in s.upper() for s in result["exact_matches"])


def test_calculate_synonym_aware_overlap_with_gaps():
    resume_skills = {"python", "k8s"}
    job_skills = {"python", "kubernetes", "docker", "aws"}

    result = calculate_synonym_aware_overlap(resume_skills, job_skills)
    # Python is exact match, k8s resolves kubernetes (2/4 = 50%)
    assert result["match_percentage"] == 50
    assert "Docker" in result["missing_skills"]
    assert "Aws" in result["missing_skills"] or "AWS" in result["missing_skills"]


def test_keyword_match_score_integration():
    resume = "Built APIs with FastAPI and deployed to K8s."
    job = "Requirements: FastAPI, Kubernetes, and Docker."

    score = calculate_keyword_match_score(resume, job, enable_synonyms=True)
    assert score["match_percentage"] >= 66  # FastAPI + K8s(Kubernetes)
    assert len(score["synonym_matches"]) > 0
