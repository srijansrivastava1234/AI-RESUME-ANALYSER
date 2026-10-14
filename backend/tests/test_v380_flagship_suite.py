"""End-to-End Integration Suite for v3.8.0 Flagship Technical Innovations.

Validates the integrated pipeline for:
1. Lever ATS Diagnostic Simulator & Fast-Tagging Engine
2. SAP SuccessFactors XML Profile Mapping Simulator
3. Binary Zero-Width Steganography & Homoglyph Attack Detector
4. EEOC 4/5ths Rule & 2-Standard-Deviation Statistical Auditor
5. Euclidean 2D Bounding Box Spatial Density & Gutter Collision Budgeter
6. Composite Multi-Service REST API Integration Matrix
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.simulators.lever import simulate_lever_parsing
from app.simulators.successfactors import simulate_successfactors_parsing
from app.adversarial_steganography import sanitize_adversarial_text
from app.eeoc_statistical_auditor import (
    calculate_two_standard_deviation_z_score,
    generate_nyc_ll144_audit_report,
)
from app.spatial_budgeter import BoundingBox, audit_canvas_spatial_budget

client = TestClient(app)


def test_lever_ats_e2e_pipeline():
    sample_resume = (
        "Jane Doe\n"
        "jane.doe@example.com | (555) 019-2834\n"
        "Staff Software Engineer with 10 years experience in Python, Kubernetes, and AWS.\n"
        "Architected distributed event streaming backend reducing latency by 45%.\n"
        "Skills: Python, TypeScript, Docker, PostgreSQL"
    )
    result = simulate_lever_parsing(sample_resume)
    assert result["engine"] == "Lever"
    assert result["is_safe"] is True
    assert result["compatibility_score"] >= 70
    assert "Senior" in result["extracted_entities"]["fast_tags"]
    assert "Python" in result["extracted_entities"]["fast_tags"]
    assert "Cloud/AWS/GCP" in result["extracted_entities"]["fast_tags"]
    assert result["extracted_entities"]["has_contact_info"] is True


def test_successfactors_ats_e2e_pipeline():
    sample_resume = (
        "John Smith\n"
        "Email: john.smith@domain.com\n"
        "Phone: (555) 987-6543\n"
        "Professional Experience\n"
        "Principal Systems Engineer - Cloud Corp (2018 - Present)\n"
        "• Scaled microservices architecture handling 50k req/sec.\n"
        "Education\n"
        "Bachelor of Science in Computer Science - University of California\n"
        "Technical Skills\n"
        "Go, Python, Terraform, CI/CD pipelines\n"
        "Certifications\n"
        "AWS Certified Solutions Architect Professional"
    )
    result = simulate_successfactors_parsing(sample_resume)
    assert result["engine"] == "SAP SuccessFactors"
    assert result["is_safe"] is True
    assert result["compatibility_score"] >= 80
    assert result["extracted_fields"]["has_contact_data"] is True
    assert "bachelor" in result["extracted_fields"]["degrees_identified"]


def test_adversarial_steganography_and_homoglyphs_e2e_pipeline():
    # Cyrillic homoglyph 'o' in Python (\u043e) and 'A' in AWS (\u0410)
    evasion_text = (
        "Senior Software Developer specializing in Pyth\u043en and \u0410WS.\n"
        "Managed large cloud infrastructure."
    )
    sanitized, report = sanitize_adversarial_text(evasion_text)
    assert "Python" in sanitized
    assert "AWS" in sanitized
    assert report["homoglyphs_detected"] == 2
    assert report["is_adversarial"] is True
    assert report["threat_score"] > 0


def test_eeoc_statistical_significance_and_ll144_e2e_pipeline():
    # Test statistically significant disparity (z > 1.96)
    z_val, is_sig = calculate_two_standard_deviation_z_score(
        selected_target=20, total_target=100,
        selected_benchmark=60, total_benchmark=100
    )
    assert is_sig is True
    assert z_val < -2.0

    # Test NYC LL 144 audit report generation
    cohort = {
        "Group_Alpha": {"total": 120, "selected": 96},  # 80%
        "Group_Beta": {"total": 100, "selected": 75},   # 75% -> 75/80 = 93.75% (> 80% four-fifths rule)
    }
    report = generate_nyc_ll144_audit_report(cohort)
    assert report["status"] == "COMPLIANT"
    assert report["is_certified"] is True
    assert report["benchmark_group"] == "Group_Alpha"
    assert len(report["violations"]) == 0


def test_spatial_budgeter_e2e_pipeline():
    boxes = [
        {"id": "header", "x": 36.0, "y": 36.0, "width": 540.0, "height": 60.0, "page": 1},
        {"id": "summary", "x": 36.0, "y": 105.0, "width": 540.0, "height": 80.0, "page": 1},
        {"id": "experience", "x": 36.0, "y": 195.0, "width": 540.0, "height": 300.0, "page": 1},
    ]
    report = audit_canvas_spatial_budget(boxes=boxes, page_format="letter", min_margin_pt=36.0)
    assert report["is_valid_layout"] is True
    assert report["status"] == "VALID"
    assert len(report["margin_violations"]) == 0
    assert len(report["collisions"]) == 0
    assert report["density_ratio"] > 0.40


def test_v380_multi_service_api_composite_matrix():
    # 1. Lever API
    res_lever = client.post("/api/simulate/lever", json={
        "resume_text": "Lead Engineer Jane Doe with Python, Docker, AWS and React experience."
    })
    assert res_lever.status_code == 200
    assert res_lever.json()["engine"] == "Lever"

    # 2. SuccessFactors API
    res_sf = client.post("/api/simulate/successfactors", json={
        "resume_text": "Contact\nj@test.com\nExperience\nStaff Eng\nEducation\nBS CS\nSkills\nGo, C++"
    })
    assert res_sf.status_code == 200
    assert res_sf.json()["engine"] == "SAP SuccessFactors"

    # 3. Adversarial Security API
    res_sec = client.post("/api/security/adversarial-audit", json={
        "resume_text": "Cloud Archit\u0435ct with K\u0443bernetes."
    })
    assert res_sec.status_code == 200
    assert res_sec.json()["report"]["homoglyphs_detected"] >= 1

    # 4. EEOC Audit API
    res_eeoc = client.post("/api/compliance/eeoc-audit", json={
        "cohort_data": {
            "Demographic_X": {"total": 50, "selected": 45},
            "Demographic_Y": {"total": 50, "selected": 42}
        }
    })
    assert res_eeoc.status_code == 200
    assert res_eeoc.json()["status"] == "COMPLIANT"

    # 5. Spatial Budget API
    res_layout = client.post("/api/layout/spatial-budget", json={
        "boxes": [
            {"id": "title", "x": 50.0, "y": 50.0, "width": 500.0, "height": 40.0, "page": 1}
        ],
        "page_format": "letter",
        "min_margin_pt": 36.0
    })
    assert res_layout.status_code == 200
    assert res_layout.json()["is_valid_layout"] is True
