import pytest
from app.header_normalizer import audit_section_headers


def test_standard_canonical_headers():
    resume_text = """
    Jane Doe
    Software Engineer

    Professional Experience
    Senior Developer at Acme Corp (2021 - Present)
    - Built distributed microservices

    Education
    B.S. in Computer Science, Stanford University

    Technical Skills
    Python, FastAPI, Docker, Kubernetes, PostgreSQL

    Projects
    High-Performance Key-Value Store

    Certifications
    AWS Certified Solutions Architect
    """
    result = audit_section_headers(resume_text)
    assert result["canonical_score"] == 100
    assert result["status"] == "ATS Compliant"
    assert len(result["missing_mandatory"]) == 0
    assert len(result["risky_creative_headers"]) == 0
    assert "Work Experience" in result["found_canonicals"]
    assert "Education" in result["found_canonicals"]
    assert "Skills" in result["found_canonicals"]


def test_risky_creative_headers_mapped():
    resume_text = """
    Alex Smith
    Full Stack Developer

    Where I've Been
    Frontend Engineer at StartupX

    Alma Mater
    B.A. in Digital Arts, NYU

    My Toolkit
    React, TypeScript, CSS3, Tailwind

    Things I've Built
    Portfolio Generator app
    """
    result = audit_section_headers(resume_text)
    assert len(result["risky_creative_headers"]) >= 3
    assert result["status"] in ("Partial Compliance", "High Risk of Parser Dropout")
    
    # Check mappings
    mapped_canonicals = [r["recommended_canonical"] for r in result["risky_creative_headers"]]
    assert "Work Experience" in mapped_canonicals
    assert "Education" in mapped_canonicals
    assert "Skills" in mapped_canonicals
    assert any("Replace non-canonical header" in rec for rec in result["recommendations"])


def test_missing_mandatory_education():
    resume_text = """
    John Doe
    Developer

    Work Experience
    DevOps Engineer at CloudCo

    Technical Skills
    Docker, Jenkins, Terraform
    """
    result = audit_section_headers(resume_text)
    assert "Education" in result["missing_mandatory"]
    assert result["canonical_score"] <= 75
    assert any("Education" in rec for rec in result["recommendations"])


def test_markdown_and_colon_formatting():
    resume_text = """
    ## Work Experience:
    Software Engineer

    ### Education:
    M.S. in Software Engineering

    # Core Competencies:
    Python, Golang, SQL
    """
    result = audit_section_headers(resume_text)
    assert "Work Experience" in result["found_canonicals"]
    assert "Education" in result["found_canonicals"]
    assert "Skills" in result["found_canonicals"]
    assert len(result["missing_mandatory"]) == 0


def test_empty_resume_text():
    result = audit_section_headers("")
    assert result["canonical_score"] == 0
    assert result["status"] == "Empty Text"
    assert len(result["missing_mandatory"]) == 3
