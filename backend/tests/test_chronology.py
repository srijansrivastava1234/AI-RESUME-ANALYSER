import pytest
from app.chronology import audit_career_chronology

def test_empty_and_whitespace_input():
    res = audit_career_chronology("")
    assert res["chronology_score"] == 0
    assert res["timeline_health"] == "Empty Document"
    assert res["total_experience_months"] == 0
    assert res["total_experience_years"] == 0.0

    res_ws = audit_career_chronology("   \n\t   ")
    assert res_ws["chronology_score"] == 0
    assert res_ws["timeline_health"] == "Empty Document"

def test_clean_standard_chronology():
    resume = (
        "Jane Doe\n"
        "Staff Software Engineer\n"
        "Experience\n"
        "Lead Architect at CloudScale\n"
        "Jan 2022 - Present\n"
        "- Scaled distributed caching layer.\n\n"
        "Senior Engineer at DataMesh\n"
        "March 2019 - Dec 2021\n"
        "- Built streaming data pipelines.\n\n"
        "Software Engineer at FirstTech\n"
        "2016-01 - 2019-02\n"
        "- Developed backend microservices in Go.\n"
    )
    res = audit_career_chronology(resume)
    assert res["chronology_score"] >= 85
    assert res["timeline_health"] == "Optimal Chronological Flow"
    assert res["detected_roles_count"] == 3
    assert res["total_experience_years"] >= 9.0
    assert len(res["career_gaps"]) == 0
    assert len(res["non_canonical_warnings"]) == 0

def test_employment_gap_detection():
    resume_with_gap = (
        "Senior Engineer at TechCo\n"
        "Jan 2023 - Present\n"
        "- Modernized cloud architecture.\n\n"
        "Engineer at OldCo\n"
        "Jan 2020 - Dec 2021\n"
        "- Maintained legacy services.\n"
    )
    res = audit_career_chronology(resume_with_gap)
    # Gap from 2021-12 to 2023-01 is ~12 months
    assert len(res["career_gaps"]) == 1
    gap = res["career_gaps"][0]
    assert gap["gap_duration_months"] >= 11
    assert "2021-12" in gap["gap_start"]
    assert "2023-01" in gap["gap_end"]
    assert "recruiter_advice" in gap
    assert res["chronology_score"] < 100

def test_overlapping_tenure_merging():
    # Two simultaneous roles: full-time and consulting
    resume_overlapping = (
        "Principal Consultant at AdviseCorp\n"
        "Jan 2021 - Dec 2022\n"
        "- Strategic architectural advisory.\n\n"
        "Senior Lead at PrimeCorp\n"
        "June 2020 - June 2022\n"
        "- Hands-on engineering leadership.\n"
    )
    res = audit_career_chronology(resume_overlapping)
    # Total span from 2020-06 to 2022-12 is 31 months (~2.6 years), NOT 24 + 25 = 49 months!
    assert 2.4 <= res["total_experience_years"] <= 2.8
    assert res["total_experience_months"] == 31
    assert len(res["career_gaps"]) == 0

def test_non_canonical_date_warnings():
    resume_seasonal = (
        "Frontend Developer\n"
        "Spring 2021 - Summer 2022\n"
        "- Built React UI components.\n\n"
        "Intern\n"
        "2 years ago - 1 year ago\n"
        "- Assisted QA team.\n"
    )
    res = audit_career_chronology(resume_seasonal)
    assert len(res["non_canonical_warnings"]) >= 2
    assert any("Spring 2021" in w for w in res["non_canonical_warnings"])
    assert any("2 years ago" in w for w in res["non_canonical_warnings"])
    assert res["chronology_score"] < 85

def test_no_dates_detected():
    resume_no_dates = (
        "Alex Smith\n"
        "Developer with extensive experience in Python, AWS, and Docker.\n"
        "Responsible for building enterprise microservices.\n"
    )
    res = audit_career_chronology(resume_no_dates)
    assert res["chronology_score"] == 50
    assert res["timeline_health"] == "No Dates Detected"
    assert res["total_experience_months"] == 0
    assert "Could not detect standard calendar date ranges" in res["recommendations"][0]

def test_mm_yyyy_date_format():
    resume_slash = (
        "Engineer at BetaCorp\n"
        "04/2021 - 10/2023\n"
        "- Deployed Kubernetes apps.\n"
    )
    res = audit_career_chronology(resume_slash)
    assert res["detected_roles_count"] == 1
    assert res["date_ranges_detected"][0]["start"] == "2021-04"
    assert res["date_ranges_detected"][0]["end"] == "2023-10"
    assert res["total_experience_months"] == 31

def test_year_only_ranges():
    resume_year = (
        "Software Engineer at BetaCorp\n"
        "2018 - 2021\n"
        "- Developed Go microservices.\n"
    )
    res = audit_career_chronology(resume_year)
    assert res["detected_roles_count"] == 1
    assert res["date_ranges_detected"][0]["start"] == "2018-01"
    assert res["date_ranges_detected"][0]["end"] == "2021-12"

def test_severe_chronology_penalties():
    resume_penalized = (
        "Role 0\n"
        "2010 - 2011\n"
        "Role 0b\n"
        "2014 - 2015\n"
        "Role 1\n"
        "2018 - 2019\n"
        "Role 2\n"
        "Spring 2021 - Summer 2022\n"
        "Role 3\n"
        "3 years ago - 2 years ago\n"
        "Role 4\n"
        "Q1 2023 - Q4 2023\n"
    )
    res = audit_career_chronology(resume_penalized)
    assert res["chronology_score"] < 65
    assert res["timeline_health"] == "Chronological Parse Risk"
