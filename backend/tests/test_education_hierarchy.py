"""Unit tests for Academic Credential Hierarchy & GPA Scale Normalizer."""

import pytest
from app.education_hierarchy import parse_education_hierarchy


def test_empty_education_text():
    res = parse_education_hierarchy("")
    assert res["highest_degree_tier"] == "NONE"
    assert res["degree_tier_level"] == 0
    assert res["ats_education_score"] == 0.0


def test_phd_candidate_stem():
    text = """
    EDUCATION
    Stanford University
    Doctor of Philosophy (Ph.D.) in Computer Science
    GPA: 3.95 / 4.0 | Expected Graduation: 2026
    Honors: Dean's List, Magna Cum Laude
    """
    res = parse_education_hierarchy(text)
    assert res["highest_degree_tier"] == "DOCTORATE"
    assert res["degree_tier_level"] == 5
    assert res["is_stem"] is True
    assert res["is_in_progress"] is True
    assert res["normalized_gpa_4_scale"] == 3.95
    assert "Computer Science" in res["majors_found"]
    assert len(res["honors_found"]) >= 1
    assert res["ats_education_score"] >= 80.0


def test_masters_with_10_point_cgpa():
    text = """
    National Institute of Technology
    Master of Technology in Information Technology
    CGPA: 9.2 / 10.0
    """
    res = parse_education_hierarchy(text)
    assert res["highest_degree_tier"] == "MASTERS"
    assert res["degree_tier_level"] == 4
    assert res["is_stem"] is True
    assert res["normalized_gpa_4_scale"] == 3.68
    assert res["raw_gpa_detected"] == "9.2/10.0 CGPA"


def test_bachelors_percentage():
    text = """
    University of Toronto
    Bachelor of Science in Mathematics
    Grade: 85%
    """
    res = parse_education_hierarchy(text)
    assert res["highest_degree_tier"] == "BACHELORS"
    assert res["degree_tier_level"] == 3
    assert res["normalized_gpa_4_scale"] == 3.4
