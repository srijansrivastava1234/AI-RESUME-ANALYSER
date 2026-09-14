import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.compliance import (
    audit_ats_compliance,
    extract_resume_bullets,
    filter_false_positive_metrics,
    SENIORITY_XYZ_TARGET_RATIOS
)
from app.agent_prompt import (
    generate_agent_refactor_prompt,
    generate_byok_export_package
)

client = TestClient(app)

SAMPLE_RESUME = """
Jane Doe
jane.doe@example.com | (555) 234-5678 | San Francisco, CA
linkedin.com/in/janedoe | github.com/janedoe

PROFESSIONAL SUMMARY
Senior Software Architect specializing in distributed cloud systems, high-throughput microservices, and AI pipelines.

WORK EXPERIENCE
Principal Cloud Engineer | Acme Cloud Systems (2021 - Present)
- Architected asynchronous event-driven streaming pipeline handling 250k req/s using FastAPI, Kafka, and Redis, cutting p99 latency by 35%.
- Engineered zero downtime automated deployment pipeline using Kubernetes and Docker, mitigating 99.9% of deployment failures.
- Spearheaded database partitioning and caching refactor with PostgreSQL, reducing AWS cloud infrastructure spend by $120k annually.

Software Engineer | DevTech Corp (2018 - 2021)
- Developed REST APIs using Python, PostgreSQL, and Docker supporting 50k active daily clients.
- Responsible for maintaining codebases and attending agile standup meetings.

TECHNICAL SKILLS
- Languages: Python, Go, TypeScript, SQL, Bash
- Frameworks: FastAPI, React, Docker, Kubernetes, Kafka, Redis, PostgreSQL, AWS

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley (2018)
"""

SAMPLE_JOB_DESC = """
We are looking for a Senior / Staff Cloud Architect with deep experience in Python, FastAPI, Docker, Kubernetes, PostgreSQL, AWS, Kafka, and Redis.
Experience in microservices architecture, latency reduction, and CI/CD pipelines is required.
"""


def test_extract_resume_bullets():
    bullets = extract_resume_bullets(SAMPLE_RESUME)
    assert len(bullets) >= 4
    assert any("Architected" in b for b in bullets)
    assert any("Engineered" in b for b in bullets)


def test_filter_false_positive_metrics():
    # Software versions must NOT count as metrics
    bullet_with_version = "Migrated service to Python 3.11 and Node v18.2.0."
    metrics = filter_false_positive_metrics(bullet_with_version, ["3.11", "18.2.0"])
    assert "3.11" not in metrics
    assert "18.2.0" not in metrics

    # Network ports and RFC standards must NOT count as metrics
    bullet_with_ports = "Configured traffic routing on Port 8080 per RFC 2616 compliance."
    metrics_port = filter_false_positive_metrics(bullet_with_ports, ["8080", "2616"])
    assert "8080" not in metrics_port
    assert "2616" not in metrics_port

    # Binary impacts must count as true positives
    bullet_binary = "Architected deployment pipeline achieving zero downtime across microservices."
    binary_metrics = filter_false_positive_metrics(bullet_binary, [])
    assert any("zero downtime" in m.lower() for m in binary_metrics)


def test_audit_ats_compliance_comprehensive():
    report = audit_ats_compliance(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JOB_DESC,
        target_seniority="senior",
        target_pages=1
    )

    assert "composite_score" in report
    assert report["composite_score"] >= 70
    assert report["letter_grade"] in ["A+", "A", "B"]
    assert report["target_seniority"] == "senior"
    assert report["target_pages"] == 1

    pillars = report["pillars"]
    assert "keywords" in pillars
    assert "xyz_impact" in pillars
    assert "structure" in pillars
    assert "density" in pillars

    # Pillar weights assert
    assert pillars["keywords"]["weight"] == 0.40
    assert pillars["xyz_impact"]["weight"] == 0.30
    assert pillars["structure"]["weight"] == 0.15
    assert pillars["density"]["weight"] == 0.15

    # Safe Harbor & Legal verification
    safe_harbor = report["regulatory_safe_harbor"]
    assert safe_harbor["is_compliant"] is True
    assert "COMPLIANT" in safe_harbor["eu_ai_act_status"]
    assert "SAFE_HARBOR_VERIFIED" in safe_harbor["nyc_ll_144_status"]
    assert "Mobley v. Workday" in safe_harbor["legal_precedent"]


def test_audit_ats_compliance_seniority_calibration():
    report_junior = audit_ats_compliance(SAMPLE_RESUME, target_seniority="junior")
    report_senior = audit_ats_compliance(SAMPLE_RESUME, target_seniority="senior")
    report_staff = audit_ats_compliance(SAMPLE_RESUME, target_seniority="staff")

    assert report_junior["pillars"]["xyz_impact"]["target_ratio"] == SENIORITY_XYZ_TARGET_RATIOS["junior"]
    assert report_senior["pillars"]["xyz_impact"]["target_ratio"] == SENIORITY_XYZ_TARGET_RATIOS["senior"]
    assert report_staff["pillars"]["xyz_impact"]["target_ratio"] == SENIORITY_XYZ_TARGET_RATIOS["staff"]


def test_audit_ats_compliance_empty_raises():
    with pytest.raises(ValueError):
        audit_ats_compliance("")


def test_agent_refactor_prompt_synthesis():
    prompt = generate_agent_refactor_prompt(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JOB_DESC,
        target_seniority="senior",
        missing_keywords=["GraphQL", "Terraform"]
    )

    assert "# ROLE: SENIOR TECHNICAL RESUME ARCHITECT" in prompt
    assert "Accomplished [X] as measured by [Y], by doing [Z]" in prompt
    assert "GraphQL, Terraform" in prompt
    assert "ANTI-FABRICATION" in prompt
    assert "ZERO FABRICATION" in prompt


def test_byok_export_package():
    compliance_report = audit_ats_compliance(SAMPLE_RESUME, target_seniority="mid")
    package = generate_byok_export_package(
        resume_text=SAMPLE_RESUME,
        compliance_report=compliance_report,
        job_description=SAMPLE_JOB_DESC
    )

    assert package["metadata"]["version"] == "1.6.0"
    assert "agent_refactor_prompt" in package
    assert "scorecard" in package
    assert package["regulatory_safe_harbor"]["is_compliant"] is True


def test_api_compliance_audit_endpoint():
    response = client.post(
        "/api/compliance-audit",
        json={
            "resume_text": SAMPLE_RESUME,
            "job_description": SAMPLE_JOB_DESC,
            "seniority": "senior",
            "target_pages": 1
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "composite_score" in data
    assert "letter_grade" in data
    assert "percentile_rank" in data
    assert "executive_summary" in data
    assert isinstance(data["percentile_rank"], (int, float))
    assert 1.0 <= data["percentile_rank"] <= 99.0
    assert "Candidate ranks in the" in data["executive_summary"]
    assert "pillars" in data
    assert "regulatory_safe_harbor" in data
    assert data["target_seniority"] == "senior"


def test_compliance_percentile_and_executive_summary():
    result = audit_ats_compliance(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JOB_DESC,
        target_seniority="staff"
    )
    assert "percentile_rank" in result
    assert "executive_summary" in result
    assert 0.0 <= result["percentile_rank"] <= 99.0
    assert "Staff" in result["executive_summary"]
    assert "Grade" in result["executive_summary"]


def test_api_agent_prompt_endpoint():
    response = client.post(
        "/api/agent-prompt",
        json={
            "resume_text": SAMPLE_RESUME,
            "job_description": SAMPLE_JOB_DESC,
            "seniority": "mid",
            "missing_keywords": ["Cassandra", "Snowflake"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "agent_prompt" in data
    assert "Cassandra, Snowflake" in data["agent_prompt"]
    assert "ANTI-FABRICATION" in data["agent_prompt"]


def test_api_analyze_endpoint_enriches_compliance():
    files = {"file": ("resume.txt", SAMPLE_RESUME.encode("utf-8"), "text/plain")}
    response = client.post("/api/analyze", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "compliance_audit" in data["report"]
    assert "byok_agent_prompt" in data["report"]
    assert "composite_score" in data["report"]["compliance_audit"]
    assert "letter_grade" in data["report"]["compliance_audit"]
