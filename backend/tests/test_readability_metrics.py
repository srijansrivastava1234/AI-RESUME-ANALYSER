"""
Unit tests for readability metrics module.
"""

from app.readability_metrics import (
    calculate_coleman_liau_index,
    calculate_automated_readability_index,
    evaluate_executive_scannability
)

SAMPLE_RESUME_PARAGRAPH = (
    "Architected high-throughput microservices in Go and Python reducing distributed transaction latency by 45%. "
    "Orchestrated Kubernetes deployments across AWS multi-region infrastructure maintaining 99.99% system availability."
)

def test_calculate_coleman_liau_index():
    cli = calculate_coleman_liau_index(SAMPLE_RESUME_PARAGRAPH)
    assert 5.0 <= cli <= 30.0
    assert calculate_coleman_liau_index("") == 0.0

def test_calculate_automated_readability_index():
    ari = calculate_automated_readability_index(SAMPLE_RESUME_PARAGRAPH)
    assert 5.0 <= ari <= 30.0
    assert calculate_automated_readability_index("") == 0.0

def test_evaluate_executive_scannability():
    res = evaluate_executive_scannability(SAMPLE_RESUME_PARAGRAPH)
    assert "composite_grade_level" in res
    assert res["scannability_score"] > 0
    assert "verdict" in res
