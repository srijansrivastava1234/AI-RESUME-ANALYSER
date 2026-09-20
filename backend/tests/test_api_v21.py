import io
import pytest
from fastapi.testclient import TestClient
from app.main import app, APP_VERSION

client = TestClient(app)

def test_health_check_version_v21():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == APP_VERSION
    assert data["status"] == "healthy"

def test_audit_layout_endpoint_success():
    payload = {
        "text": (
            "Skills: Python, Go        Acme Corp - Lead Engineer\n"
            "Tools: Docker, K8s        Architected multi-region cloud cluster\n"
            "Contact: jane@test.com    Decreased API latency by 45% using Redis\n"
        )
    }
    response = client.post("/api/audit-layout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "linearization_score" in data
    assert "risk_tier" in data
    assert "gutter_anomaly_count" in data
    assert data["gutter_anomaly_count"] >= 3
    assert len(data["simulated_scrambled_snippets"]) > 0

def test_audit_layout_endpoint_validation():
    # Empty JSON
    response = client.post("/api/audit-layout", json={})
    assert response.status_code == 422

    # Missing text field
    response = client.post("/api/audit-layout", json={"other": "content"})
    assert response.status_code == 422

def test_audit_chronology_endpoint_success():
    payload = {
        "text": (
            "Staff Engineer at CloudScale\n"
            "Jan 2022 - Present\n"
            "- Led infrastructure engineering.\n\n"
            "Senior Engineer at DataCorp\n"
            "March 2019 - Dec 2021\n"
            "- Managed Kubernetes clusters.\n"
        )
    }
    response = client.post("/api/audit-chronology", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "chronology_score" in data
    assert "timeline_health" in data
    assert "total_experience_years" in data
    assert data["detected_roles_count"] == 2
    assert data["total_experience_years"] >= 6.0

def test_audit_chronology_endpoint_validation():
    response = client.post("/api/audit-chronology", json={})
    assert response.status_code == 422

def test_audit_font_integrity_endpoint_success():
    payload = {
        "text": (
            "Architected an e\uFB03cient work\uFB02ow with \uE001 FontAwesome icons and de\uFB01ned standards."
        )
    }
    response = client.post("/api/audit-font-integrity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "font_health_score" in data
    assert "iso_19005_compliant" in data
    assert "ligature_count" in data
    assert data["ligature_count"] >= 3
    assert data["pua_glyph_count"] == 1
    assert data["iso_19005_compliant"] is False
    assert len(data["recovered_words"]) >= 2

def test_audit_font_integrity_endpoint_validation():
    response = client.post("/api/audit-font-integrity", json={})
    assert response.status_code == 422

def test_analyze_endpoint_includes_v21_audits():
    sample_resume = (
        "Jane Doe\n"
        "Senior Cloud Architect\n"
        "Experience\n"
        "Tech Lead at AlphaCorp\n"
        "Jan 2021 - Present\n"
        "- Architected multi-region Kubernetes platform handling 50k RPS.\n"
        "Skills: Python, Go, Docker, AWS, Terraform\n"
    )
    files = {
        "file": ("jane_doe_resume.txt", io.BytesIO(sample_resume.encode("utf-8")), "text/plain")
    }
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert "report" in res_data
    report = res_data["report"]
    assert "layout_linearization" in report
    assert "career_chronology" in report
    assert "font_integrity" in report
    assert report["layout_linearization"]["linearization_score"] >= 80
    assert report["career_chronology"]["detected_roles_count"] >= 1
    assert report["font_integrity"]["iso_19005_compliant"] is True
