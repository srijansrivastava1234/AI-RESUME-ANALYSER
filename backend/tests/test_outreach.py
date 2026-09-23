"""
Test suite for Phase 6: Tailored Cover Letter, Cold Outreach, and InMail Generator.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.outreach import (
    generate_deterministic_outreach,
    generate_outreach,
    _extract_key_accomplishments,
    _extract_candidate_identity,
    _extract_target_context
)

SAMPLE_RESUME = """
SARAH CONNOR
Los Angeles, CA | sarah.connor@example.com | (555) 987-6543 | linkedin.com/in/sarahconnor

SUMMARY
Senior DevOps & Infrastructure Engineer with 8+ years leading cloud security and Kubernetes migrations.

EXPERIENCE
Lead DevOps Engineer | Cyberdyne Systems | 2020 - Present
• Engineered multi-region AWS Kubernetes architecture cutting cloud spend by $45,000 monthly.
• Automated zero-trust security scanning across 120+ microservices achieving 99.99% uptime.

EDUCATION
B.S. in Computer Engineering | UCLA | 2016
"""

SAMPLE_JD = """
Job Title: Senior Cloud Infrastructure Engineer
Company: Sentinel Defense Tech
Location: Remote

We are seeking a seasoned Cloud Engineer to scale our distributed Kubernetes infrastructure and automate multi-cloud deployments.
Required Skills: AWS, Docker, Kubernetes, Terraform, Python, CI/CD.
"""

client = TestClient(app)

def test_extract_accomplishments():
    bullets = _extract_key_accomplishments(SAMPLE_RESUME)
    assert len(bullets) >= 1
    assert any("$45,000" in b or "99.99%" in b for b in bullets)

def test_extract_candidate_identity():
    identity = _extract_candidate_identity(SAMPLE_RESUME)
    assert "Sarah Connor" in identity["name"] or "SARAH CONNOR" in identity["name"]
    assert identity["email"] == "sarah.connor@example.com"

def test_extract_target_context():
    context = _extract_target_context(SAMPLE_JD)
    assert "Cloud" in context["role"] or "Engineer" in context["role"]
    assert "Sentinel" in context["company"] or "Sentinel Defense Tech" in context["company"]

def test_deterministic_cover_letter():
    res = generate_deterministic_outreach(
        resume_text=SAMPLE_RESUME,
        job_desc=SAMPLE_JD,
        mode="cover_letter",
        tone="confident",
        recipient_name="Alex Vance",
        company_name="Sentinel Defense Tech"
    )
    assert res["mode"] == "cover_letter"
    assert "Dear Alex Vance" in res["body"]
    assert "Sentinel Defense Tech" in res["body"]
    assert "$45,000" in res["body"] or "99.99%" in res["body"]
    assert res["word_count"] > 50

def test_deterministic_linkedin_inmail():
    res = generate_deterministic_outreach(
        resume_text=SAMPLE_RESUME,
        job_desc=SAMPLE_JD,
        mode="linkedin_inmail",
        tone="direct",
        recipient_name="John Recruiter",
        company_name="Sentinel Defense Tech"
    )
    assert res["mode"] == "linkedin_inmail"
    assert "Hi John Recruiter" in res["body"]
    assert "10-minute chat" in res["body"] or "brief" in res["body"]

def test_deterministic_cold_email():
    res = generate_deterministic_outreach(
        resume_text=SAMPLE_RESUME,
        job_desc=SAMPLE_JD,
        mode="cold_email",
        tone="technical",
        recipient_name="Tech Lead",
        company_name="Sentinel Defense Tech"
    )
    assert res["mode"] == "cold_email"
    assert "Subject:" not in res["body"] # Subject is in separate field
    assert "Sentinel Defense Tech" in res["subject"]
    assert "Attached is my resume" in res["body"]

def test_deterministic_follow_up():
    res = generate_deterministic_outreach(
        resume_text=SAMPLE_RESUME,
        job_desc=SAMPLE_JD,
        mode="follow_up",
        tone="executive",
        recipient_name="Hiring Manager",
        company_name="Sentinel Defense Tech"
    )
    assert res["mode"] == "follow_up"
    assert "follow up" in res["body"].lower()

def test_async_generate_outreach_fallback():
    res = asyncio.run(generate_outreach(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        mode="cover_letter",
        tone="confident"
    ))
    assert res["mode"] == "cover_letter"
    assert len(res["body"]) > 100

def test_api_generate_outreach_endpoint():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_description": SAMPLE_JD,
        "mode": "cover_letter",
        "tone": "confident",
        "recipient_name": "Marcus Wright",
        "company_name": "Resistance AI"
    }
    res = client.post("/api/generate-outreach", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "cover_letter"
    assert "Marcus Wright" in data["body"]
    assert "Resistance AI" in data["body"]
    assert data["word_count"] > 50
