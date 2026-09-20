"""
Regression and integration test suite verifying v2.2.0 enhancements in analyzer pipeline.
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.analyzer import analyze_resume
from app.main import app

client = TestClient(app)

SAMPLE_RESUME = (
    "Alex Mercer\n"
    "Email: alex.mercer@gmail.com | Phone: +1-555-456-7890\n"
    "LinkedIn: https://linkedin.com/in/alexmercer GitHub: https://github.com/alexmercer\n\n"
    "SUMMARY\n"
    "Senior Cloud Architect with 8+ years experience designing scalable distributed systems.\n\n"
    "EXPERIENCE\n"
    "Staff Platform Engineer | CloudTech (2021 - Present)\n"
    "- Architected Kubernetes clusters on AWS serving 15M monthly active users with 99.99% uptime.\n"
    "- Implemented Redis distributed caching reducing database load by 40% and cutting API latency to 45ms.\n"
    "- Automated CI/CD deployment pipelines using Docker, Python, and GitHub Actions.\n\n"
    "SKILLS\n"
    "Python, Docker, Kubernetes, AWS, Redis, PostgreSQL, Team Player, Fast Learner\n\n"
    "EDUCATION\n"
    "B.S. in Computer Science | Stanford University (2017)\n"
)


def test_analyze_resume_contains_v22_keys():
    result = analyze_resume(SAMPLE_RESUME, "Senior Cloud Engineer requiring Python, Kubernetes, AWS, and Docker.")
    assert "bm25_audit" in result
    assert "contact_audit" in result
    assert "skill_classification" in result


def test_analyze_resume_bm25_structure():
    result = analyze_resume(SAMPLE_RESUME, "Python Docker Kubernetes AWS")
    bm25 = result["bm25_audit"]
    assert "raw_bm25_score" in bm25
    assert "normalized_score" in bm25
    assert "keyword_coverage" in bm25
    assert "term_breakdown" in bm25
    assert bm25["keyword_coverage"] > 0
    assert len(bm25["term_breakdown"]) > 0


def test_analyze_resume_contact_structure():
    result = analyze_resume(SAMPLE_RESUME)
    contact = result["contact_audit"]
    assert "reliability_index" in contact
    assert "status" in contact
    assert contact["status"] == "OPTIMAL"
    assert contact["email_audit"]["email"] == "alex.mercer@gmail.com"
    assert contact["phone_audit"]["is_valid"] is True


def test_analyze_resume_skill_classification_structure():
    result = analyze_resume(SAMPLE_RESUME)
    skills = result["skill_classification"]
    assert "hard_skills" in skills
    assert "soft_skills" in skills
    assert "hard_ratio" in skills
    assert "credibility_index" in skills
    assert skills["hard_ratio"] > 0.0


def test_end_to_end_analyze_endpoint_v22_payload():
    file_bytes = SAMPLE_RESUME.encode("utf-8")
    files = {
        "file": ("alex_mercer_resume.txt", io.BytesIO(file_bytes), "text/plain")
    }
    data = {
        "job_description": "We are seeking a Senior Cloud Engineer proficient in Python, Docker, Kubernetes, and AWS."
    }
    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert "report" in res_data
    report = res_data["report"]
    assert "bm25_audit" in report
    assert "contact_audit" in report
    assert "skill_classification" in report
    assert report["bm25_audit"]["normalized_score"] > 0
    assert report["contact_audit"]["reliability_index"] >= 80
