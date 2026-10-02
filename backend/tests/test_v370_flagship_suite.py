"""End-to-end Integration Test Suite for v3.7.0 Flagship Technical Innovations.

Validates the full pipeline for:
1. Metric Verifiability & Baseline Denominator Calibrator
2. Academic Credential Hierarchy & GPA Normalizer
3. Cognitive Load & Readability Index Engine (Gunning Fog, Coleman-Liau, ARI)
4. Prompt Injection & Zero-Width Steganography Auditor
5. Leadership Trajectory & Organizational Scope Profiler
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_metric_consistency_api_flow():
    payload = {
        "resume_text": "Engineered event-driven pipeline in Python and Kafka, reducing latency by 45% from 200ms to 110ms and saving $80k annually."
    }
    response = client.post("/api/audit/metric-consistency", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verifiability_score"] > 60.0
    assert data["baseline_attached_count"] >= 1
    assert data["metric_breakdown"]["percentages"] >= 1
    assert data["metric_breakdown"]["currency"] >= 1


def test_education_hierarchy_api_flow():
    payload = {
        "resume_text": "Master of Science in Computer Science, Stanford University. GPA: 3.88 / 4.0. Magna Cum Laude."
    }
    response = client.post("/api/audit/education-hierarchy", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["highest_degree_tier"] == "MASTERS"
    assert data["normalized_gpa_4_scale"] == 3.88
    assert data["is_stem"] is True
    assert len(data["honors_found"]) >= 1


def test_cognitive_load_api_flow():
    payload = {
        "resume_text": "Designed high-throughput REST API with FastAPI and PostgreSQL, serving 10M daily requests with 99.99% uptime."
    }
    response = client.post("/api/audit/cognitive-load", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["gunning_fog_index"] > 0.0
    assert data["cognitive_load_score"] > 50.0
    assert data["skimmability_rating"] in ["OPTIMAL_SKIMMABILITY", "GOOD_SKIMMABILITY", "MODERATE_COGNITIVE_STRAIN"]


def test_prompt_injection_api_flow():
    payload = {
        "resume_text": "Normal resume content without malicious payloads.\nLed software engineering team."
    }
    response = client.post("/api/audit/prompt-injection", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_safe"] is True
    assert data["threat_level"] == "CLEAN"
    assert data["security_score"] == 100.0


def test_leadership_profile_api_flow():
    payload = {
        "resume_text": (
            "Principal Engineer & Tech Lead\n"
            "- Architected cloud architecture and authored system RFCs.\n"
            "- Mentored 6 engineers and managed sprint deliverable execution.\n"
            "- Partnered with Product executives on technical strategy."
        )
    }
    response = client.post("/api/audit/leadership-profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_leadership_score"] >= 60.0
    assert "STAFF" in data["inferred_leadership_tier"] or "TECH_LEAD" in data["inferred_leadership_tier"] or "DIRECTOR" in data["inferred_leadership_tier"]
