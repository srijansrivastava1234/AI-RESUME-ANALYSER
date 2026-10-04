import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_RESUME = """
Jane Doe
jane.doe@example.com | (555) 123-4567 | linkedin.com/in/janedoe

Professional Summary
Senior Python and Distributed Systems Architect with 7+ years of experience.

Work Experience
Lead Backend Architect - CloudScale
Jan 2020 - Present
- Architected distributed microservices handling 250k RPS on AWS.
- Mentored team of 8 engineers and improved sprint velocity by 30%.
- Reduced database p99 latency from 120ms to 45ms using Redis.

Education
B.S. in Computer Science - State University
2015 - 2019

Skills
Python, FastAPI, AWS, Docker, Kubernetes, PostgreSQL, Kafka, Redis
"""

def test_api_simulate_multi_ats():
    response = client.post("/api/simulate/ats", json={"resume_text": SAMPLE_RESUME})
    assert response.status_code == 200
    data = response.json()
    assert "overall_cross_ats_score" in data
    assert "engines" in data
    assert "icims" in data["engines"]
    assert "workday" in data["engines"]
    assert "greenhouse" in data["engines"]
    assert "taleo" in data["engines"]
    assert data["overall_cross_ats_score"] >= 80

def test_api_simulate_icims():
    response = client.post("/api/simulate/icims", json={"resume_text": SAMPLE_RESUME})
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "iCIMS Enterprise"
    assert data["compatibility_score"] >= 80
    assert data["is_safe"] is True

def test_api_simulate_workday():
    response = client.post("/api/simulate/workday", json={"resume_text": SAMPLE_RESUME})
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "Workday"
    assert data["compatibility_score"] >= 80

def test_api_simulate_greenhouse():
    response = client.post("/api/simulate/greenhouse", json={"resume_text": SAMPLE_RESUME})
    assert response.status_code == 200
    data = response.json()
    assert "Greenhouse" in data["engine"]
    assert data["compatibility_score"] >= 80

def test_api_simulate_taleo():
    response = client.post("/api/simulate/taleo", json={"resume_text": SAMPLE_RESUME})
    assert response.status_code == 200
    data = response.json()
    assert "Taleo" in data["engine"]
    assert data["compatibility_score"] >= 80
