import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_RESUME = """John Doe
john@example.com

Summary
Full stack engineer with 5 years experience in Python and React.

Work Experience
Senior Software Engineer at Alpha Corp (2021 - Present)
- Architected cloud data pipelines using AWS and Terraform.
- Engineered FastAPI microservices reducing p99 latency by 30%.
- Deployed Docker containers via GitHub Actions CI/CD workflows.

Skills
Python, FastAPI, React, TypeScript, Docker, PostgreSQL

Education
B.S. in Computer Science (2017 - 2021)
"""

def test_audit_section_flow_endpoint():
    response = client.post("/api/audit-section-flow", json={
        "resume_text": SAMPLE_RESUME,
        "is_early_career": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "flow_score" in data
    assert "detected_sequence" in data
    assert data["is_optimal"] is True

def test_audit_action_verbs_endpoint():
    response = client.post("/api/audit-action-verbs", json={
        "resume_text": SAMPLE_RESUME
    })
    assert response.status_code == 200
    data = response.json()
    assert "action_verb_score" in data
    assert "variety_ratio" in data
    assert "tier_breakdown" in data
    assert data["total_bullets_analyzed"] >= 3

def test_audit_page_budget_endpoint():
    response = client.post("/api/audit-page-budget", json={
        "resume_text": SAMPLE_RESUME,
        "target_pages": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "budget_score" in data
    assert "spillover_detected" in data
    assert "metrics" in data
    assert "fractional_pages" in data["metrics"]

def test_version_bump_v23():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] >= "2.3.0"
