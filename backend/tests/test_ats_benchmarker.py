import pytest
from app.ats_benchmarker import benchmark_ats_parsing_resilience

def test_benchmark_ats_empty():
    res = benchmark_ats_parsing_resilience("")
    assert res["resilience_score"] == 0
    assert res["resilience_grade"] == "F"
    assert len(res["missing_critical_sections"]) == 3

def test_benchmark_ats_complete_resume():
    sample = """
    Jane Doe
    Email: jane.doe@example.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/janedoe

    Professional Experience:
    Senior Software Engineer | TechCorp (Jan 2022 – Present)
    - Architected distributed data ingestion engine reducing compute costs by 35%.

    Education:
    Bachelor of Science in Computer Science, University of California (2018 - 2022)

    Technical Skills:
    Python, FastAPI, Docker, Kubernetes, PostgreSQL, AWS
    """
    res = benchmark_ats_parsing_resilience(sample)
    assert res["resilience_score"] >= 85
    assert res["resilience_grade"] in ["A", "A+"]
    assert res["contact_detection"]["email_detected"] is True
    assert res["contact_detection"]["phone_detected"] is True
    assert res["contact_detection"]["linkedin_detected"] is True
    assert len(res["missing_critical_sections"]) == 0
    assert res["engine_breakdown"]["workday"]["status"] == "Optimal"
    assert res["engine_breakdown"]["greenhouse"]["status"] == "Optimal"

def test_benchmark_ats_missing_contact_and_headers():
    broken_sample = """
    Random Project Description
    Built a frontend interface using HTML and CSS.
    """
    res = benchmark_ats_parsing_resilience(broken_sample)
    assert res["resilience_score"] < 60
    assert res["contact_detection"]["email_detected"] is False
    assert len(res["missing_critical_sections"]) > 0

def test_benchmark_ats_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.post("/api/audit/ats-benchmark", json={
        "resume_text": "Jane Doe\nEmail: jane@example.com\nExperience:\nSoftware Engineer (2022 - Present)\nEducation:\nBS CS\nSkills:\nPython"
    })
    assert response.status_code == 200
    data = response.json()
    assert "resilience_score" in data
    assert "engine_breakdown" in data

