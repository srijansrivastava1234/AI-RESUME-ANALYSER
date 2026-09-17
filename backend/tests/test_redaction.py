import pytest
from app.redaction import anonymize_resume_for_blind_audit

class TestCandidateRedaction:
    def test_empty_and_whitespace_text(self):
        result = anonymize_resume_for_blind_audit("")
        assert result["total_redactions"] == 0
        assert result["sanitized_text"] == ""
        assert result["safe_harbor_certified"] is False

        result_ws = anonymize_resume_for_blind_audit("   \n\t  ")
        assert result_ws["total_redactions"] == 0
        assert result_ws["safe_harbor_certified"] is False

    def test_redact_contact_details(self):
        sample_text = (
            "Jane Developer\n"
            "Email: jane.dev@company.org | Phone: (415) 555-2671\n"
            "LinkedIn: https://www.linkedin.com/in/janedev\n"
            "GitHub: https://github.com/janedev-code\n"
            "San Francisco, CA 94105\n"
        )
        result = anonymize_resume_for_blind_audit(sample_text)
        assert result["total_redactions"] >= 5
        assert "[EMAIL REDACTED]" in result["sanitized_text"]
        assert "jane.dev@company.org" not in result["sanitized_text"]
        assert "[PHONE REDACTED]" in result["sanitized_text"]
        assert "(415) 555-2671" not in result["sanitized_text"]
        assert "[LINKEDIN REDACTED]" in result["sanitized_text"]
        assert "[GITHUB REDACTED]" in result["sanitized_text"]
        assert "[ZIP CODE REDACTED]" in result["sanitized_text"]
        assert result["safe_harbor_certified"] is True

    def test_redact_candidate_name_header(self):
        sample_text = (
            "Robert C. Martin\n"
            "Senior Systems Architect with 10 years experience."
        )
        result = anonymize_resume_for_blind_audit(sample_text)
        assert result["redacted_entities_count"]["candidate_name"] == 1
        assert "[CANDIDATE NAME REDACTED]" in result["sanitized_text"]
        assert "Robert C. Martin" not in result["sanitized_text"]

    def test_redact_graduation_age_proxies(self):
        sample_text = (
            "Education:\n"
            "Stanford University - B.S. in Computer Science, 2012\n"
            "Graduated Class of 2008 from Tech High School\n"
            "Master of Science, 2015\n"
        )
        result = anonymize_resume_for_blind_audit(sample_text)
        assert result["redacted_entities_count"]["graduation_age_proxies"] >= 2
        assert "[GRADUATION YEAR REDACTED - AGE PROXY DEFENSE]" in result["sanitized_text"]
        assert "2012" not in result["sanitized_text"]

    def test_technical_accomplishments_preserved(self):
        sample_text = (
            "David Miller\n"
            "david@mail.com\n"
            "Architected distributed data platform on AWS with Kubernetes and Python.\n"
            "Reduced p99 query latency by 45% and generated $320,000 in operational cost savings.\n"
            "Docker, PostgreSQL, Redis, Kafka, React 19."
        )
        result = anonymize_resume_for_blind_audit(sample_text)
        sanitized = result["sanitized_text"]

        # PII should be removed
        assert "David Miller" not in sanitized
        assert "david@mail.com" not in sanitized

        # Technical merit, tools, and metrics MUST remain 100% intact
        assert "AWS" in sanitized
        assert "Kubernetes" in sanitized
        assert "Python" in sanitized
        assert "45%" in sanitized
        assert "$320,000" in sanitized
        assert "PostgreSQL" in sanitized
        assert "Redis" in sanitized
        assert "Kafka" in sanitized
        assert "React 19" in sanitized

    def test_compliance_metadata_and_safe_harbor(self):
        sample = "Alice Smith\nEngineer\nemail: alice@test.io"
        result = anonymize_resume_for_blind_audit(sample)
        assert result["safe_harbor_certified"] is True
        assert result["audit_dossier_ready"] is True
        assert any("NYC Local Law 144" in f for f in result["compliance_frameworks"])
        assert any("EEOC" in f for f in result["compliance_frameworks"])
        assert any("EU AI Act" in f for f in result["compliance_frameworks"])
