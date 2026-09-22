import pytest
from app.skill_recency import analyze_skill_recency


def test_empty_skill_recency():
    res = analyze_skill_recency("")
    assert res["recency_score"] == 0.0
    assert res["status"] == "PASS"


def test_modern_active_stack():
    text = """
    Software Engineer (2023 - Present)
    Built distributed microservices with Python, FastAPI, Docker, and Kubernetes on AWS.
    Implemented real-time event pipelines using Kafka and PostgreSQL.
    """
    res = analyze_skill_recency(text, current_year=2026)
    assert res["recency_score"] >= 85.0
    assert res["is_active_career"] is True
    assert "fastapi" in res["modern_skills_detected"]
    assert "docker" in res["modern_skills_detected"]
    assert len(res["legacy_skills_detected"]) == 0
    assert res["status"] == "EXCELLENT"


def test_legacy_stack_detection():
    text = """
    Developer (2008 - 2012)
    Maintained web applications in AngularJS, ColdFusion, and Flash with Subversion (SVN).
    """
    res = analyze_skill_recency(text, current_year=2026)
    assert len(res["legacy_skills_detected"]) >= 3
    assert "coldfusion" in res["legacy_skills_detected"]
    assert "flash" in res["legacy_skills_detected"]
    assert res["recency_score"] < 70.0
    assert res["status"] == "WARNING"
