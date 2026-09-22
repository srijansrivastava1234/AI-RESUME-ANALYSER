import pytest
from app.metric_diversity import analyze_metric_diversity


def test_empty_metric_text():
    res = analyze_metric_diversity("")
    assert res["diversity_score"] == 0.0
    assert res["dimensions_covered"] == 0
    assert res["status"] == "FAIL"


def test_high_diversity_metrics():
    text = """
    - Spearheaded engineering of cloud payments gateway driving $1.5M in annual ARR.
    - Optimized database query caching, reducing p99 latency from 450ms to 45ms (90% reduction).
    - Scaled real-time WebSocket cluster to support 500k DAU and 10M daily requests.
    - Led and mentored a cross-functional squad of 8 software engineers.
    """
    res = analyze_metric_diversity(text)
    assert res["dimensions_covered"] >= 4
    assert res["diversity_score"] >= 80.0
    assert res["status"] == "EXCELLENT"
    assert "financial" in res["covered_categories"]
    assert "percentage" in res["covered_categories"]
    assert "scale_volume" in res["covered_categories"]
    assert "velocity_time" in res["covered_categories"]


def test_single_dimension_metrics():
    text = """
    - Improved test coverage by 15%.
    - Increased customer conversion by 25%.
    """
    res = analyze_metric_diversity(text)
    assert res["dimensions_covered"] == 1
    assert "percentage" in res["covered_categories"]
    assert "financial" in res["missing_dimensions"]
    assert res["status"] == "WARNING"


def test_zero_metrics():
    text = "Responsible for building web pages and debugging bugs in Python."
    res = analyze_metric_diversity(text)
    assert res["dimensions_covered"] == 0
    assert res["status"] == "CRITICAL"
