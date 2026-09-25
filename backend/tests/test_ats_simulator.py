import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.simulators.workday import simulate_workday_parsing
from app.simulators.greenhouse import simulate_greenhouse_parsing
from app.simulators.taleo import simulate_taleo_parsing
from app.ats_simulator import run_multi_ats_simulation

client = TestClient(app)

SAMPLE_RESUME_TEXT = """
Alex Johnson
alex.johnson@example.com | +1 (555) 019-2834 | linkedin.com/in/alexjohnson
San Francisco, CA

PROFESSIONAL SUMMARY
Senior Full Stack Engineer with 6+ years of experience architecting cloud systems with AWS and Kubernetes.

WORK EXPERIENCE
Staff Software Engineer | CloudScale Tech (2021 - Present)
• Architected high-throughput microservices in Python and FastAPI, reducing P99 latency by 45%.
• Led migration from on-premise servers to AWS (Amazon Web Services), cutting annual cloud costs by $180,000.
• Mentored 8 software engineers on Docker containerization and CI/CD pipelines.

EDUCATION
B.S. in Computer Science | University of California, Berkeley (2015 - 2019)

SKILLS
Python, FastAPI, React, TypeScript, Docker, Kubernetes, AWS, PostgreSQL, Redis, CI/CD
"""

def test_simulate_workday_parsing():
    res = simulate_workday_parsing(SAMPLE_RESUME_TEXT)
    assert res["engine"] == "Workday"
    assert res["compatibility_score"] >= 80
    assert res["extracted_entities"]["email"] == "alex.johnson@example.com"
    assert res["extracted_entities"]["experience_detected"] is True
    assert res["extracted_entities"]["education_detected"] is True
    assert res["is_safe"] is True


def test_simulate_workday_parsing_multi_column_trap():
    bad_column_text = """
    Jane Doe
    Skills: Python, AWS        Work Experience: Lead Developer
    Skills: Docker, Redis      Company: Acme Corp (2020-2023)
    Skills: React, Node        Managed 5 engineers
    Page 1 of 2
    """
    res = simulate_workday_parsing(bad_column_text)
    assert res["compatibility_score"] < 90
    assert any("multi-column" in h.lower() for h in res["hazards"])
    assert any("stripped" in h.lower() for h in res["hazards"])  # Stripped "Page 1 of 2"


def test_simulate_greenhouse_parsing():
    res = simulate_greenhouse_parsing(SAMPLE_RESUME_TEXT)
    assert res["engine"] == "Greenhouse / Lever"
    assert res["compatibility_score"] >= 80
    assert res["extracted_entities"]["bullet_count"] >= 3
    assert res["extracted_entities"]["total_skills_detected"] >= 5
    assert "Cloud & DevOps" in res["extracted_entities"]["skill_clusters"]


def test_simulate_greenhouse_parsing_artifacts():
    dirty_text = "Software Engineer \uE005 \uFFFD \u200B at ScaleFlow Systems with no bullets"
    res = simulate_greenhouse_parsing(dirty_text)
    assert res["compatibility_score"] < 80
    assert any("unicode" in h.lower() or "artifact" in h.lower() for h in res["hazards"])


def test_simulate_taleo_parsing():
    res = simulate_taleo_parsing(SAMPLE_RESUME_TEXT)
    assert res["engine"] == "Taleo / Oracle"
    assert res["compatibility_score"] >= 75
    # In sample resume, AWS has 'Amazon Web Services' expanded, but K8s / GCP might not be present
    assert len(res["hazards"]) <= 2


def test_simulate_taleo_parsing_creative_headers():
    creative_text = """
    Dev Hero
    Where I've Worked
    Built cool stuff with K8s and GCP.
    """
    res = simulate_taleo_parsing(creative_text)
    assert res["compatibility_score"] < 80
    assert any("non-standard section headers" in h.lower() for h in res["hazards"])
    assert any("unexpanded acronym" in h.lower() for h in res["hazards"])


def test_run_multi_ats_simulation_composite():
    res = run_multi_ats_simulation(SAMPLE_RESUME_TEXT)
    assert res["overall_cross_ats_score"] >= 80
    assert "Universal ATS Compatible" in res["tier"]
    assert "workday" in res["engines"]
    assert "greenhouse" in res["engines"]
    assert "taleo" in res["engines"]


def test_simulate_ats_empty_input():
    res = run_multi_ats_simulation("")
    assert res is not None
    assert "overall_cross_ats_score" in res
    assert res["overall_cross_ats_score"] <= 50
    assert "Empty" in res["tier"] or "Risk" in res["tier"]



def test_api_simulate_ats_endpoint():
    response = client.post(
        "/api/simulate-ats",
        json={"resume_text": SAMPLE_RESUME_TEXT}
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_cross_ats_score" in data
    assert "tier" in data
    assert "engines" in data
    assert data["engines"]["workday"]["engine"] == "Workday"
    assert data["engines"]["greenhouse"]["engine"] == "Greenhouse / Lever"
    assert data["engines"]["taleo"]["engine"] == "Taleo / Oracle"

