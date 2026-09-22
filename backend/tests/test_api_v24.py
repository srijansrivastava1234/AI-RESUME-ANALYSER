import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_readability():
    response = client.post("/api/audit-readability", json={
        "resume_text": "Architected distributed systems with Python and Kubernetes on AWS. Scaled backend API to handle 10M daily requests."
    })
    assert response.status_code == 200
    data = response.json()
    assert "flesch_reading_ease" in data
    assert "flesch_kincaid_grade" in data
    assert data["word_count"] > 0


def test_api_voice():
    response = client.post("/api/audit-voice", json={
        "resume_text": "Architected high-speed microservices using FastAPI and Docker. Was responsible for database backups."
    })
    assert response.status_code == 200
    data = response.json()
    assert "passive_density_pct" in data
    assert "active_ratio_pct" in data
    assert data["total_sentences"] >= 2


def test_api_cliches():
    response = client.post("/api/audit-cliches", json={
        "resume_text": "A hardworking rockstar and team player developer."
    })
    assert response.status_code == 200
    data = response.json()
    assert "cliche_count" in data
    assert data["cliche_count"] >= 2


def test_api_metric_diversity():
    response = client.post("/api/audit-metric-diversity", json={
        "resume_text": "Scaled API to 500k DAU generating $1.2M ARR and reduced latency by 35% across a team of 6 engineers."
    })
    assert response.status_code == 200
    data = response.json()
    assert "diversity_score" in data
    assert data["dimensions_covered"] >= 3


def test_api_filename():
    response = client.post("/api/audit-filename", json={
        "filename": "Alex_Smith_Resume.pdf",
        "candidate_name": "Alex Smith"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["score"] == 100.0


def test_api_skill_recency():
    response = client.post("/api/audit-skill-recency", json={
        "resume_text": "Software Engineer (2024 - Present). Built services using FastAPI, Docker, and Kubernetes.",
        "current_year": 2026
    })
    assert response.status_code == 200
    data = response.json()
    assert "recency_score" in data
    assert data["is_active_career"] is True


def test_api_bullet_lengths():
    response = client.post("/api/audit-bullet-lengths", json={
        "resume_text": "• Architected high-throughput microservices using FastAPI, Docker, and PostgreSQL, increasing system reliability by 35%.\n• Spearheaded transition from legacy monolithic codebase to event-driven Kafka messaging."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_bullets"] == 2
    assert "scannability_score" in data


def test_api_summary_style():
    response = client.post("/api/audit-summary-style", json={
        "summary_text": "Senior Software Engineer with 7+ years of experience specializing in cloud infrastructure and distributed microservices."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["style"] == "MODERN_VALUE_SUMMARY"


def test_api_salary_disclosures():
    response = client.post("/api/audit-salary-disclosures", json={
        "resume_text": "Current CTC: 25 LPA. Expected Salary: $150,000 / year."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["has_salary_disclosure"] is True
    assert data["disclosures_count"] >= 2


def test_api_portfolio_links():
    response = client.post("/api/audit-portfolio-links", json={
        "resume_text": "LinkedIn: https://linkedin.com/in/alexsmith | GitHub: https://github.com/alexsmith"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["has_linkedin"] is True
    assert data["has_github"] is True
