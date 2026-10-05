import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_simulate_lever_endpoint():
    payload = {
        "resume_text": "Jane Doe\njane@example.com\n(555) 123-4567\nSenior Backend Engineer with Python and AWS experience."
    }
    response = client.post("/api/simulate/lever", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "Lever"
    assert "Senior" in data["extracted_entities"]["fast_tags"]
    assert "Python" in data["extracted_entities"]["fast_tags"]

def test_api_simulate_successfactors_endpoint():
    payload = {
        "resume_text": "Bob Smith\nbob@test.com\n(555) 000-1111\nWork Experience\nSoftware Engineer (2020 - 2024)\nEducation\nBachelor of Science in CS\nSkills\nPython, Docker"
    }
    response = client.post("/api/simulate/successfactors", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "SAP SuccessFactors"
    assert data["is_safe"] is True

def test_api_adversarial_security_audit():
    # Cyrillic lookalike 'o'
    payload = {
        "resume_text": "Expert in Pyth\u043en programming."
    }
    response = client.post("/api/security/adversarial-audit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Python" in data["sanitized_text"]
    assert data["report"]["homoglyphs_detected"] == 1

def test_api_eeoc_compliance_audit():
    payload = {
        "cohort_data": {
            "Group_A": {"total": 100, "selected": 80},
            "Group_B": {"total": 100, "selected": 75}
        },
        "scoring_threshold": 70.0
    }
    response = client.post("/api/compliance/eeoc-audit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLIANT"
    assert data["is_certified"] is True

def test_api_spatial_budget_audit():
    payload = {
        "boxes": [
            {"id": "header", "x": 36.0, "y": 36.0, "width": 540.0, "height": 60.0, "page": 1},
            {"id": "body", "x": 36.0, "y": 105.0, "width": 540.0, "height": 300.0, "page": 1}
        ],
        "page_format": "letter",
        "min_margin_pt": 36.0
    }
    response = client.post("/api/layout/spatial-budget", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VALID"
    assert data["is_valid_layout"] is True
