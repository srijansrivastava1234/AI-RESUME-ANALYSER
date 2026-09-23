import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.interview_prep import (
    generate_fallback_interview_prep,
    generate_interview_prep
)

client = TestClient(app)

SAMPLE_RESUME = """
Alex Johnson
Senior Software Engineer
San Francisco, CA | alex@example.com

EXPERIENCE
CloudScale Systems - Senior Developer (2021 - Present)
• Architected microservices with Python and FastAPI, reducing latency by 40%.
• Built distributed caching layer with Redis.
• Led team of 6 engineers on cloud deployment.

SKILLS
Python, FastAPI, Redis, Docker, SQL
"""

SAMPLE_JD = """
Staff Platform Engineer - FinTech Corp
Requirements:
- 7+ years of experience with Python, Kubernetes, AWS, and Apache Kafka.
- Experience leading incident response and large-scale architectural migrations.
"""

def test_generate_fallback_interview_prep_structure():
    res = generate_fallback_interview_prep(SAMPLE_RESUME, SAMPLE_JD, seniority="staff")
    assert res["overall_readiness_score"] > 0
    assert "readiness_tier" in res
    assert "summary_analysis" in res
    assert len(res["questions"]) == 5

    for q in res["questions"]:
        assert "id" in q
        assert "theme" in q
        assert "difficulty" in q
        assert "recruiter_intent" in q
        assert "question" in q
        assert "star_strategy" in q
        assert "situation" in q["star_strategy"]
        assert "task" in q["star_strategy"]
        assert "action" in q["star_strategy"]
        assert "result" in q["star_strategy"]
        assert "pitfall_to_avoid" in q


def test_generate_fallback_interview_prep_detects_gap():
    # JD mentions Kubernetes and Kafka which are missing from Alex's resume
    res = generate_fallback_interview_prep(SAMPLE_RESUME, SAMPLE_JD, seniority="senior")
    q1 = res["questions"][0]
    # Check that missing tech is referenced
    assert "Kubernetes" in q1["theme"] or "Kafka" in q1["theme"] or "Tech Stack" in q1["theme"]


def test_generate_interview_prep_empty():
    res = asyncio.run(generate_interview_prep(""))
    assert res["overall_readiness_score"] == 0
    assert len(res["questions"]) == 0


def test_generate_interview_prep_async():
    res = asyncio.run(generate_interview_prep(SAMPLE_RESUME, SAMPLE_JD, "senior"))
    assert res["overall_readiness_score"] >= 75
    assert len(res["questions"]) == 5


def test_api_interview_prep_endpoint():
    response = client.post(
        "/api/interview-prep",
        json={
            "resume_text": SAMPLE_RESUME,
            "job_description": SAMPLE_JD,
            "seniority": "senior"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_readiness_score" in data
    assert "questions" in data
    assert len(data["questions"]) == 5
