import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agent_prompt import generate_agent_refactor_prompt, generate_byok_export_package

client = TestClient(app)

SAMPLE_RESUME = """
Jane Doe
jane.doe@example.com | (555) 234-5678
EXPERIENCE
Software Engineer | Acme Inc
- Responsible for helping team write code.
- Worked on database fixes.
"""

SAMPLE_JD = "Looking for a Senior Backend Engineer proficient in Python, FastAPI, and Kubernetes."


def test_general_template_default():
    prompt = generate_agent_refactor_prompt(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        target_seniority="senior",
        missing_keywords=["FastAPI", "Kubernetes"],
        target_model="general"
    )
    assert "# ROLE: SENIOR TECHNICAL RESUME ARCHITECT" in prompt
    assert "FastAPI, Kubernetes" in prompt
    assert "ZERO FABRICATION" in prompt


def test_claude_template_xml_structure():
    prompt = generate_agent_refactor_prompt(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        target_seniority="staff",
        missing_keywords=["Kafka"],
        target_model="claude"
    )
    assert "<system>" in prompt
    assert "<context>" in prompt
    assert "<job_description>" in prompt
    assert "<bullets_to_refactor>" in prompt
    assert "<rules>" in prompt
    assert "Kafka" in prompt


def test_cursor_template_syntax():
    prompt = generate_agent_refactor_prompt(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        target_seniority="senior",
        missing_keywords=["Docker"],
        target_model="cursor"
    )
    assert "/* CURSOR COMPOSER: RESUME REFACTORING INSTRUCTION */" in prompt
    assert "Senior" in prompt
    assert "Docker" in prompt


def test_gpt_template_structure():
    prompt = generate_agent_refactor_prompt(
        resume_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        target_seniority="mid",
        missing_keywords=["Redis"],
        target_model="gpt"
    )
    assert "SYSTEM: RESUME OPTIMIZATION AGENT (GPT-4o)" in prompt
    assert "Redis" in prompt


def test_byok_export_package_structure():
    mock_compliance = {
        "letter_grade": "A",
        "composite_score": 92,
        "target_seniority": "senior",
        "target_pages": 1,
        "pillars": {
            "keywords": {"missing_keywords": ["GraphQL"]}
        },
        "regulatory_safe_harbor": {"is_compliant": True}
    }
    package = generate_byok_export_package(
        resume_text=SAMPLE_RESUME,
        compliance_report=mock_compliance,
        job_description=SAMPLE_JD
    )
    assert package["metadata"]["compliance_grade"] == "A"
    assert "agent_refactor_prompt" in package
    assert package["regulatory_safe_harbor"]["is_compliant"] is True


def test_api_agent_prompt_with_target_model():
    res = client.post(
        "/api/agent-prompt",
        json={
            "resume_text": SAMPLE_RESUME,
            "job_description": SAMPLE_JD,
            "seniority": "senior",
            "missing_keywords": ["FastAPI"],
            "target_model": "claude"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["target_model"] == "claude"
    assert "<system>" in data["agent_prompt"]
    assert "<rules>" in data["agent_prompt"]
