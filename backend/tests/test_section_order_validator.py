"""
Unit tests for ATS section order validator.
"""

from app.section_order_validator import audit_section_order, normalize_section_type

def test_normalize_section_type():
    assert normalize_section_type("Professional Summary") == "SUMMARY"
    assert normalize_section_type("Work History") == "EXPERIENCE"
    assert normalize_section_type("Core Competencies") == "SKILLS"
    assert normalize_section_type("Hobbies & Passions") == "OTHER"

def test_audit_section_order_compliant():
    sections = ["Contact Info", "Professional Summary", "Work Experience", "Technical Skills", "Education"]
    res = audit_section_order(sections)
    assert res["is_compliant"] is True
    assert res["score"] == 100
    assert len(res["violations"]) == 0

def test_audit_section_order_violation():
    sections = ["Education", "Work Experience", "Skills"]
    res = audit_section_order(sections)
    assert res["is_compliant"] is False
    assert res["score"] < 100
    assert len(res["violations"]) > 0
