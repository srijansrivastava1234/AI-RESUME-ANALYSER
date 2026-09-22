import pytest
from app.voice_detector import analyze_voice


def test_empty_voice_text():
    res = analyze_voice("")
    assert res["total_sentences"] == 0
    assert res["passive_count"] == 0
    assert res["status"] == "PASS"


def test_fully_active_voice_text():
    text = """
    - Architected scalable Kubernetes microservices processing 1M daily requests.
    - Spearheaded migration of legacy monolith to FastAPI and PostgreSQL.
    - Mentored 6 junior engineers on unit testing and continuous integration.
    """
    res = analyze_voice(text)
    assert res["total_sentences"] == 3
    assert res["passive_count"] == 0
    assert res["active_ratio_pct"] == 100.0
    assert res["status"] == "EXCELLENT"


def test_passive_voice_detection():
    text = """
    - Was responsible for managing database backups.
    - Microservices were deployed by the team using Jenkins.
    - Was tasked with customer support tickets.
    - Worked on improving frontend page load speed.
    """
    res = analyze_voice(text)
    assert res["total_sentences"] >= 4
    assert res["passive_count"] >= 3
    assert len(res["passive_instances"]) >= 3
    assert res["status"] in ["WARNING", "CRITICAL"]
    assert any("responsible for" in inst["flagged_phrase"].lower() for inst in res["passive_instances"])


def test_mixed_voice_text():
    text = """
    - Spearheaded development of AI recommendation engine.
    - Helped to fix minor styling issues in CSS.
    - Deployed new GraphQL gateway across 4 regions.
    """
    res = analyze_voice(text)
    assert res["total_sentences"] == 3
    assert res["passive_count"] == 1
    assert res["active_ratio_pct"] > 60.0
