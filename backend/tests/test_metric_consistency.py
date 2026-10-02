"""Unit tests for Metric Verifiability & Baseline Denominator Calibrator."""

import pytest
from app.metric_consistency import audit_metric_verifiability


def test_empty_resume_text():
    res = audit_metric_verifiability("")
    assert res["verifiability_score"] == 0.0
    assert res["total_metrics_found"] == 0
    assert len(res["recommendations"]) > 0


def test_high_verifiability_metrics():
    text = """
    - Reduced API response time by 45% from 220ms to 121ms across 50 microservices, saving $120k annually.
    - Scaled distributed database throughput from 10k to 500k req/sec, achieving 5x performance improvement.
    - Led team of 12 engineers delivering 15 pull requests weekly with 99.9% uptime SLA.
    """
    res = audit_metric_verifiability(text)
    assert res["verifiability_score"] > 60.0
    assert res["total_metrics_found"] >= 5
    assert res["baseline_attached_count"] >= 2
    assert res["baseline_attachment_rate"] > 0.4
    assert res["metric_breakdown"]["currency"] >= 1
    assert res["metric_breakdown"]["percentages"] >= 1
    assert res["metric_breakdown"]["multipliers"] >= 1
    assert len(res["implausible_claims"]) == 0


def test_unbounded_implausible_claims():
    text = """
    - Built platform with 0 bugs and 10000% speed improvement for infinite scalability.
    """
    res = audit_metric_verifiability(text)
    assert len(res["implausible_claims"]) >= 1
    assert res["verifiability_score"] < 50.0


def test_missing_baselines():
    text = """
    - Increased customer satisfaction by 40%.
    - Boosted conversion by 25%.
    - Improved deployment speed by 50%.
    """
    res = audit_metric_verifiability(text)
    assert res["baseline_attached_count"] == 0
    assert res["baseline_attachment_rate"] == 0.0
    assert any("Missing baseline denominators" in r for r in res["recommendations"])
