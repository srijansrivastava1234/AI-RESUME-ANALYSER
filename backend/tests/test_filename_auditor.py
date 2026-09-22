import pytest
from app.filename_auditor import audit_filename


def test_empty_filename():
    res = audit_filename("")
    assert res["is_valid"] is False
    assert res["status"] == "FAIL"


def test_perfect_canonical_filename():
    res = audit_filename("Alex_Smith_Software_Engineer_Resume.pdf")
    assert res["is_valid"] is True
    assert res["status"] == "EXCELLENT"
    assert res["score"] == 100.0
    assert len(res["hazards"]) == 0


def test_generic_and_spaced_filename():
    res = audit_filename("my resume (1) #final.pdf", candidate_name="Jane Doe")
    assert res["is_valid"] is False
    assert res["score"] < 70.0
    assert any("spaces" in h.lower() for h in res["hazards"])
    assert any("hazardous" in h.lower() for h in res["hazards"])
    assert res["suggested_filename"] == "Jane_Doe_Resume.pdf"


def test_multi_dot_and_extension_hazard():
    res = audit_filename("resume.v2.final.exe")
    assert res["is_valid"] is False
    assert any("extension" in h.lower() for h in res["hazards"])
    assert any("dot" in h.lower() for h in res["hazards"])
