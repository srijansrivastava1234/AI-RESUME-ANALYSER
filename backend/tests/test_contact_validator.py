"""
Unit test suite for candidate contact coordinates and link security auditor.
"""

import pytest
from app.contact_validator import (
    audit_email,
    audit_phone,
    audit_profile_links,
    audit_candidate_contact,
)


def test_audit_email_valid_and_rfc_compliance():
    res = audit_email("alex.dev@gmail.com")
    assert res["is_valid"] is True
    assert res["is_placeholder"] is False
    assert res["penalty"] == 0
    assert res["issue"] is None

    # Invalid RFC syntax
    res_bad = audit_email("alex.dev@invalid@com")
    assert res_bad["is_valid"] is False
    assert res_bad["penalty"] > 0


def test_audit_email_placeholder_and_disposable():
    res_ph = audit_email("yourname@email.com")
    assert res_ph["is_placeholder"] is True
    assert res_ph["penalty"] == 25

    res_disp = audit_email("candidate@mailinator.com")
    assert res_disp["is_disposable"] is True
    assert res_disp["penalty"] == 40

    res_missing = audit_email("")
    assert res_missing["is_valid"] is False
    assert res_missing["penalty"] == 35


def test_audit_phone_e164_formatting():
    res = audit_phone("+1 555-234-5678")
    assert res["is_valid"] is True
    assert res["has_country_code"] is True
    assert res["e164_formatted"] == "+15552345678"
    assert res["penalty"] == 0

    res_intl = audit_phone("+91 9876543210")
    assert res_intl["is_valid"] is True
    assert res_intl["e164_formatted"] == "+919876543210"
    assert res_intl["penalty"] == 0


def test_audit_phone_missing_country_code_and_placeholder():
    # Missing country code
    res_no_code = audit_phone("555-234-5678")
    assert res_no_code["is_valid"] is True
    assert res_no_code["has_country_code"] is False
    assert res_no_code["penalty"] == 10
    assert "Missing international country calling code" in res_no_code["issue"]

    # Placeholder phone number
    res_ph = audit_phone("123-456-7890")
    assert res_ph["is_placeholder"] is True
    assert res_ph["penalty"] == 25


def test_audit_profile_links_https_and_platforms():
    links = [
        "https://linkedin.com/in/alexdeveloper",
        "https://github.com/alexdev99",
        "http://alex-portfolio.dev"
    ]
    results = audit_profile_links(links)
    assert len(results) == 3
    assert results[0]["type"] == "LinkedIn"
    assert results[0]["is_https"] is True
    assert results[0]["penalty"] == 0

    assert results[1]["type"] == "GitHub"
    assert results[1]["is_https"] is True

    # Insecure HTTP
    assert results[2]["is_https"] is False
    assert results[2]["penalty"] == 15
    assert any("Insecure protocol" in issue for issue in results[2]["issues"])


def test_audit_profile_links_shorteners_and_placeholders():
    links = [
        "https://bit.ly/my-resume-link",
        "https://linkedin.com/in/yourname"
    ]
    results = audit_profile_links(links)
    assert results[0]["is_shortener"] is True
    assert results[0]["penalty"] == 25

    assert results[1]["is_placeholder"] is True
    assert results[1]["penalty"] == 20


def test_audit_candidate_contact_from_raw_text():
    resume_header = (
        "Jane Doe\n"
        "Email: jane.doe.tech@domain.org\n"
        "Phone: +1 (415) 890-1234\n"
        "Profiles: https://linkedin.com/in/janedoe-cloud https://github.com/janedoe-cloud\n"
    )
    audit = audit_candidate_contact(text=resume_header)
    assert audit["reliability_index"] >= 90
    assert audit["status"] == "OPTIMAL"
    assert audit["email_audit"]["is_valid"] is True
    assert audit["phone_audit"]["has_country_code"] is True
    assert len(audit["links_audit"]) == 2


def test_audit_candidate_contact_reliability_index():
    # Severely compromised contact header
    audit_bad = audit_candidate_contact(
        email="yourname@email.com",
        phone="123-456-7890",
        links=["http://bit.ly/my-profile", "https://linkedin.com/in/username"]
    )
    assert audit_bad["reliability_index"] < 60
    assert audit_bad["status"] == "CRITICAL"
    assert len(audit_bad["recommendations"]) >= 3
