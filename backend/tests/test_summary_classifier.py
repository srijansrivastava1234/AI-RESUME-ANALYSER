import pytest
from app.summary_classifier import classify_summary_style


def test_empty_summary():
    res = classify_summary_style("")
    assert res["style"] == "MISSING"
    assert res["modernity_score"] == 0.0


def test_outdated_objective_statement():
    text = (
        "OBJECTIVE: Seeking a challenging position in a progressive IT organization "
        "where I can utilize my skills and grow for mutual growth."
    )
    res = classify_summary_style(text)
    assert res["style"] == "OUTDATED_OBJECTIVE"
    assert res["modernity_score"] <= 30.0
    assert res["status"] == "CRITICAL"
    assert len(res["objective_markers_detected"]) > 0


def test_modern_executive_summary():
    text = (
        "Senior Software Engineer with 6+ years of experience specializing in distributed systems, "
        "cloud infrastructure, and microservices. Proven track record of scaling high-throughput APIs."
    )
    res = classify_summary_style(text)
    assert res["style"] == "MODERN_VALUE_SUMMARY"
    assert res["modernity_score"] == 100.0
    assert res["status"] == "EXCELLENT"
    assert len(res["value_markers_detected"]) > 0


def test_hybrid_summary():
    text = (
        "Backend Developer with 3+ years experience looking for a full-time position to utilize my knowledge."
    )
    res = classify_summary_style(text)
    assert res["style"] == "HYBRID_MIXED"
    assert res["status"] == "WARNING"
