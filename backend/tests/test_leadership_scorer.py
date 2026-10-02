"""Unit tests for Leadership Trajectory & Scope Profiler."""

import pytest
from app.leadership_scorer import profile_leadership_trajectory


def test_empty_resume():
    res = profile_leadership_trajectory("")
    assert res["overall_leadership_score"] == 0.0
    assert res["inferred_leadership_tier"] == "INDIVIDUAL_CONTRIBUTOR"


def test_staff_plus_leadership():
    text = """
    EXPERIENCE
    Staff Software Engineer & Tech Lead
    - Architected next-generation streaming platform and authored 6 technical RFCs adopted by 120 engineers.
    - Mentored 8 software engineers, conducted 30+ technical interviews, and managed team sprint delivery.
    - Partnered with Product and Design directors to align quarterly engineering roadmap with executive strategy.
    - Reduced AWS cloud spend budget by $350k annually through automated cluster right-sizing.
    - Open source maintainer of high-throughput Kafka client library with 2k GitHub stars.
    """
    res = profile_leadership_trajectory(text)
    assert res["overall_leadership_score"] >= 75.0
    assert res["inferred_leadership_tier"] in ["STAFF_PRINCIPAL_OR_ENGINEERING_MANAGER", "DIRECTOR_OR_VP"]
    assert res["dimension_scores"]["PEOPLE_MANAGEMENT"]["score"] >= 70.0
    assert res["dimension_scores"]["TECHNICAL_GOVERNANCE"]["score"] >= 70.0
    assert res["dimension_scores"]["RESOURCE_STEWARDSHIP"]["score"] >= 45.0
    assert len(res["evidence_snippets"]) >= 3


def test_early_career_individual_contributor():
    text = """
    Junior Developer
    - Implemented frontend forms in React and fixed CSS bugs in repository.
    - Wrote unit tests in Jest for authentication handlers.
    """
    res = profile_leadership_trajectory(text)
    assert res["overall_leadership_score"] < 30.0
    assert res["inferred_leadership_tier"] == "INDIVIDUAL_CONTRIBUTOR"
    assert any("Highlight mentorship" in r for r in res["recommendations"])
