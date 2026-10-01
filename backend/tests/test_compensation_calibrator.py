import pytest
from app.compensation_calibrator import calibrate_compensation, TIER_BENCHMARKS

def test_empty_resume():
    res = calibrate_compensation("")
    assert res["seniority_tier"] == "L3"
    assert res["base_salary_median"] > 0
    assert len(res["compensation_levers"]) > 0

def test_junior_profile():
    resume = "Software Engineer Intern (2025 - 2026). Contributed bug fixes in Python."
    res = calibrate_compensation(resume, years_experience=1.0)
    assert res["seniority_tier"] == "L3"
    assert "Junior" in res["tier_title"]
    assert res["base_salary_median"] >= 90000

def test_senior_profile_with_scale():
    resume = """
    Senior Software Engineer (2018 - 2025)
    - Led a team of 6 engineers to re-architect microservices serving 10 million daily active users.
    - Reduced p99 API latency by 45% and saved $350k in annual cloud infrastructure spend.
    - Mentored junior engineers and designed distributed Kafka pipelines handling 50k QPS.
    """
    res = calibrate_compensation(resume, years_experience=7.0)
    assert res["seniority_tier"] in ["L5", "L6"]
    assert res["scope_multiplier"] > 1.0
    assert res["detected_signals"]["leadership_count"] >= 2
    assert res["detected_signals"]["scale_indicators_count"] >= 2
    assert res["detected_signals"]["quantified_metrics_count"] >= 2
    assert res["total_compensation_median"] >= 230000

def test_staff_tier_promotion():
    resume = """
    Staff Principal Architect (2012 - 2026)
    - Directed technical strategy, roadmaps, and cross-functional engineering initiatives across 4 squads.
    - Spearheaded distributed multi-region Kubernetes platform serving billions of requests with 99.99% uptime.
    - Saved $2.5M in operational costs and boosted throughput by 300%.
    """
    res = calibrate_compensation(resume, years_experience=14.0)
    assert res["seniority_tier"] == "L7"
    assert res["total_compensation_median"] >= 500000
