import pytest
from app.cliche_detector import audit_cliches, CLICHE_CATALOG


def test_empty_cliche_text():
    res = audit_cliches("")
    assert res["cliche_count"] == 0
    assert res["cleanliness_score"] == 100.0
    assert res["status"] == "PASS"


def test_clean_professional_text():
    text = (
        "Architected distributed data streaming pipeline using Kafka and Spark, "
        "processing 250k events per second with 99.99% uptime."
    )
    res = audit_cliches(text)
    assert res["cliche_count"] == 0
    assert res["cleanliness_score"] == 100.0
    assert res["status"] == "EXCELLENT"


def test_cliche_detection_and_suggestions():
    text = (
        "A hardworking and results-oriented team player and rockstar developer who thinks outside the box."
    )
    res = audit_cliches(text)
    assert res["cliche_count"] >= 4
    assert res["unique_cliches"] >= 4
    assert res["cleanliness_score"] < 80.0
    assert res["status"] in ["WARNING", "CRITICAL"]

    phrases = [item["phrase"] for item in res["detected_cliches"]]
    assert "team player" in phrases
    assert "hardworking" in phrases
    assert "rockstar" in phrases
    assert "outside the box" in phrases
