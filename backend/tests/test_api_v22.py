"""
Integration test suite for v2.2.0 REST endpoints:
- POST /api/audit-bm25
- POST /api/audit-contact
- POST /api/classify-skills
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_audit_bm25_endpoint_success():
    payload = {
        "resume_text": (
            "Senior Backend Engineer with deep expertise in Python, FastAPI, Docker, and PostgreSQL. "
            "Engineered scalable microservices architecture on AWS and Kubernetes."
        ),
        "target_keywords": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS"]
    }
    response = client.post("/api/audit-bm25", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "raw_bm25_score" in data
    assert "normalized_score" in data
    assert "keyword_coverage" in data
    assert data["keyword_coverage"] == 100.0
    assert data["matched_keywords"] == 5
    assert len(data["term_breakdown"]) == 5


def test_audit_bm25_endpoint_validation():
    # Missing required target_keywords
    response = client.post("/api/audit-bm25", json={"resume_text": "Sample text"})
    assert response.status_code == 422

    # Empty payload
    response_empty = client.post("/api/audit-bm25", json={})
    assert response_empty.status_code == 422


def test_audit_contact_endpoint_success():
    payload = {
        "email": "alex.dev@gmail.com",
        "phone": "+1 (555) 345-6789",
        "links": ["https://linkedin.com/in/alex-engineer", "https://github.com/alex-dev"]
    }
    response = client.post("/api/audit-contact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reliability_index" in data
    assert "status" in data
    assert data["reliability_index"] >= 90
    assert data["status"] == "OPTIMAL"
    assert data["email_audit"]["is_valid"] is True
    assert data["phone_audit"]["has_country_code"] is True
    assert len(data["links_audit"]) == 2


def test_audit_contact_endpoint_text_extraction():
    payload = {
        "text": (
            "Alex Smith\n"
            "alex.smith.tech@outlook.com | +1 415-555-0192\n"
            "https://linkedin.com/in/alexsmith https://github.com/alexsmith\n"
        )
    }
    response = client.post("/api/audit-contact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email_audit"]["email"] == "alex.smith.tech@outlook.com"
    assert data["phone_audit"]["is_valid"] is True
    assert len(data["links_audit"]) == 2


def test_audit_contact_endpoint_security_warning():
    payload = {
        "email": "candidate@mailinator.com",
        "phone": "555-1234",
        "links": ["http://insecure-domain.org", "https://bit.ly/my-resume"]
    }
    response = client.post("/api/audit-contact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CRITICAL"
    assert data["email_audit"]["is_disposable"] is True
    assert any(link["is_shortener"] for link in data["links_audit"])
    assert any(link["is_https"] is False for link in data["links_audit"])


def test_classify_skills_endpoint_success():
    payload = {
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Team Player", "Critical Thinking"]
    }
    response = client.post("/api/classify-skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "credibility_index" in data
    assert "hard_skills_count" in data
    assert "soft_skills_count" in data
    assert data["hard_skills_count"] == 4
    assert data["soft_skills_count"] == 2
    assert len(data["hard_skills"]) == 4
    assert len(data["soft_skills"]) == 2


def test_classify_skills_endpoint_substantiation():
    payload = {
        "skills": ["Python", "Docker", "Kubernetes", "Kafka"],
        "experience_text": "Built Python backend microservices and packaged container images with Docker."
    }
    response = client.post("/api/classify-skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["substantiation_rate"] == 50.0
    assert "Python" in data["substantiated_skills"]
    assert "Docker" in data["substantiated_skills"]
    assert "Kubernetes" in data["unsubstantiated_skills"]
    assert "Kafka" in data["unsubstantiated_skills"]


def test_classify_skills_endpoint_validation():
    # Missing skills list
    response = client.post("/api/classify-skills", json={})
    assert response.status_code == 422
