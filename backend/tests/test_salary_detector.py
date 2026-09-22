import pytest
from app.salary_detector import detect_salary_disclosures


def test_empty_salary_detector():
    res = detect_salary_disclosures("")
    assert res["has_salary_disclosure"] is False
    assert res["disclosures_count"] == 0
    assert res["status"] == "PASS"


def test_clean_resume_without_salary():
    text = (
        "Architected distributed payment gateway generating $2.5M in annual ARR. "
        "Managed a cloud infrastructure budget of $400k across AWS regions."
    )
    res = detect_salary_disclosures(text)
    assert res["has_salary_disclosure"] is False
    assert res["disclosures_count"] == 0
    assert res["status"] == "EXCELLENT"


def test_confidential_salary_disclosure_detected():
    text = """
    Software Engineer at TechCorp
    Current CTC: 24 LPA
    Expected Salary: $140,000 / year
    Hourly Rate: $75/hr
    """
    res = detect_salary_disclosures(text)
    assert res["has_salary_disclosure"] is True
    assert res["disclosures_count"] >= 2
    assert res["status"] == "CRITICAL"
    assert any("140" in item or "24" in item or "75" in item for item in res["flagged_instances"])
