import pytest
from app.skill_decay import calculate_skill_decay_score, profile_skill_decay

def test_calculate_skill_decay_score_active():
    # 0 years inactive should yield 100%
    assert calculate_skill_decay_score(0, "rapid_moving") == 100.0
    assert calculate_skill_decay_score(0, "standard_tech") == 100.0
    assert calculate_skill_decay_score(0, "evergreen") == 100.0

def test_calculate_skill_decay_score_half_life():
    # After exactly half_life years, score should be ~50.0%
    score_rapid = calculate_skill_decay_score(2.5, "rapid_moving")
    assert 49.0 <= score_rapid <= 51.0

    score_std = calculate_skill_decay_score(4.0, "standard_tech")
    assert 49.0 <= score_std <= 51.0

    score_evergreen = calculate_skill_decay_score(8.0, "evergreen")
    assert 49.0 <= score_evergreen <= 51.0

def test_profile_empty_resume():
    res = profile_skill_decay("")
    assert res["freshness_index"] == 100.0
    assert res["skills_profiled"] == 0

def test_profile_recent_skills():
    resume = """
    Senior Software Engineer (2024 - 2026)
    - Architected scalable microservices in Python, FastAPI, and Docker.
    - Optimized PostgreSQL queries and deployed Kubernetes clusters.
    """
    res = profile_skill_decay(resume, reference_year=2026)
    assert res["freshness_index"] >= 85.0
    assert res["grade"] in ["A+", "A"]
    assert len(res["active_skills"]) >= 3
    assert len(res["dormant_skills"]) == 0

def test_profile_stale_legacy_skills():
    resume = """
    Software Developer (2015 - 2018)
    - Built web apps using Angular and Django with MongoDB.
    """
    res = profile_skill_decay(resume, reference_year=2026)
    assert res["skills_profiled"] >= 2
    # Skills from 2018 in 2026 are 8 years old
    assert any(s["status"] in ["decaying", "dormant"] for s in res["decaying_skills"] + res["dormant_skills"])
