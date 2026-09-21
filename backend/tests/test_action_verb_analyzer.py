import pytest
from app.action_verb_analyzer import audit_action_verbs, extract_bullet_leading_verbs

def test_high_variety_action_verbs():
    sample = """
    - Architected multi-region cloud infrastructure using Terraform and AWS.
    - Engineered high-speed gRPC microservices reducing API latency by 45%.
    - Deployed automated CI/CD pipelines with GitHub Actions and Docker.
    - Optimized database indexing in PostgreSQL resulting in 3x throughput.
    - Spearheaded team transition to event-driven Kafka architecture.
    """
    result = audit_action_verbs(sample)
    assert result["action_verb_score"] >= 90
    assert result["variety_ratio"] == 1.0
    assert len(result["fatigued_verbs"]) == 0
    assert len(result["weak_verbs_detected"]) == 0
    assert result["tier_breakdown"]["executive"] >= 2
    assert result["tier_breakdown"]["engineering"] >= 3

def test_repetitive_verb_fatigue():
    sample = """
    - Managed daily agile standups and sprint planning sessions.
    - Managed client communications and stakeholder presentations.
    - Managed bug backlog and QA release verification workflows.
    - Managed database backup scripts and monitoring alerts.
    """
    result = audit_action_verbs(sample)
    assert result["action_verb_score"] < 80
    assert len(result["fatigued_verbs"]) > 0
    assert result["fatigued_verbs"][0]["verb"] == "managed"
    assert result["fatigued_verbs"][0]["count"] == 4

def test_weak_passive_verbs_detection():
    sample = """
    - Helped the senior engineer with database migrations.
    - Assisted in creating frontend React components.
    - Worked on testing API endpoints with Postman.
    - Responsible for fixing CSS alignment issues.
    """
    result = audit_action_verbs(sample)
    assert result["action_verb_score"] < 75
    assert len(result["weak_verbs_detected"]) >= 3
    assert any(w["verb"] in ["helped", "assisted", "worked on", "responsible for"] for w in result["weak_verbs_detected"])

def test_empty_bullets():
    result = audit_action_verbs("")
    assert result["total_bullets_analyzed"] == 0
    assert result["action_verb_score"] == 50
