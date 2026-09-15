import pytest
from app.viewport import audit_first_third_viewport


def test_audit_first_third_viewport_empty():
    res = audit_first_third_viewport("")
    assert res["status"] == "EMPTY_DOCUMENT"
    assert res["viewport_precision_score"] == 0
    assert len(res["recommendations"]) > 0


def test_audit_first_third_viewport_short():
    res = audit_first_third_viewport("Software engineer with Python experience.")
    assert res["status"] == "SHORT_DOCUMENT"
    assert res["total_words"] < 30


def test_audit_first_third_viewport_front_loaded():
    # Long resume text with strong metrics and verbs in the top 30%
    viewport_part = """
    John Doe - Staff Cloud Architect
    Architected high-throughput distributed ingestion pipelines processing 45,000 requests/sec,
    reducing latency by 42% across 8 production clusters. Spearheaded microservices migration
    saving $1.4M in cloud expenditure through optimized AWS auto-scaling configurations.
    """
    remainder_part = """
    Experience Continued:
    Senior Developer at Alpha Corp from 2018 to 2021.
    Collaborated with product teams on daily feature delivery and standard backlog grooming.
    Participated in agile ceremonies, peer code reviews, and customer demo presentations.
    Maintained documentation across internal Confluence pages and updated engineering standards.
    Supported on-call rotation schedules and triaged customer tickets within SLA targets.
    Assisted team leads with quarterly sprint capacity planning and roadmap alignment.
    Coordinated with QA analysts to ensure end-to-end regression validation.
    """
    full_resume = viewport_part + remainder_part
    res = audit_first_third_viewport(full_resume, target_skills=["AWS", "Python"])

    assert res["viewport_precision_score"] >= 80
    assert res["status"] == "EXCELLENT_PRECISION"
    assert res["viewport_metrics_count"] >= 2
    assert res["viewport_verbs_count"] >= 2
    assert res["front_loaded_metrics_ratio"] > 0.5
    assert "AWS" in res["detected_viewport_skills"]


def test_audit_first_third_viewport_back_loaded():
    # Fluffy top 30%, metrics buried at bottom
    viewport_part = """
    Professional Summary:
    Dedicated and passionate team player with a strong background in software development.
    Seeking an opportunity to utilize my extensive problem-solving skills in a dynamic environment.
    Responsible for collaborating with various cross-functional stakeholders and attending agile standups.
    Assisted teammates with routine tasks and attended weekly architecture design discussions.
    """
    remainder_part = """
    Work Experience:
    Staff Infrastructure Engineer at ScaleTech.
    Engineered automated CI/CD deployment pipelines cutting build times by 75% across 200 repositories.
    Optimized PostgreSQL database query throughput by 50% using connection pooling and indexing.
    Achieved 99.99% system availability while reducing monthly AWS infrastructure spend by $85,000.
    Mentored 12 junior engineers and established zero-downtime canary deployment strategies.
    Authored 15 technical design specifications adopted as company-wide standards.
    """
    full_resume = viewport_part + remainder_part
    res = audit_first_third_viewport(full_resume)

    # Metrics should be mostly in remainder
    assert res["remainder_metrics_count"] > res["viewport_metrics_count"]
    assert any("Recruiter 6-Second Alert" in r or "Accomplishment Burying" in r for r in res["recommendations"])
