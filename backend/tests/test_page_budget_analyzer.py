import pytest
from app.page_budget_analyzer import audit_page_budget, estimate_page_metrics

def test_optimal_single_page_budget():
    # Construct a solid 450 word / 48 line single page resume text
    lines = [f"Bullet line {i} describing an engineering achievement with FastAPI and Kubernetes." for i in range(46)]
    sample = "\n".join(lines)
    
    result = audit_page_budget(sample, target_pages=1)
    assert result["budget_score"] >= 85
    assert result["is_within_budget"] is True
    assert result["spillover_detected"] is False
    assert 0.8 <= result["metrics"]["fractional_pages"] <= 1.05

def test_spillover_hazard_detection():
    # Construct a 56 line resume that spills over into page 2 (approx 1.12 pages)
    lines = [f"Bullet line {i} explaining another metric-driven accomplishment." for i in range(56)]
    sample = "\n".join(lines)
    
    result = audit_page_budget(sample, target_pages=1)
    assert result["spillover_detected"] is True
    assert result["budget_score"] < 75
    assert any("Spillover Hazard" in w for w in result["warnings"])

def test_sparse_content_penalty():
    sample = "John Doe\nSoftware Engineer\nOnly two lines of experience."
    result = audit_page_budget(sample, target_pages=1)
    assert result["budget_score"] < 90
    assert result["metrics"]["total_words"] < 100

def test_two_page_target_compliance():
    lines = [f"Experience bullet {i} detailing senior engineering leadership in distributed systems." for i in range(95)]
    sample = "\n".join(lines)
    
    result = audit_page_budget(sample, target_pages=2)
    assert result["budget_score"] >= 80
    assert 1.7 <= result["metrics"]["fractional_pages"] <= 2.1
