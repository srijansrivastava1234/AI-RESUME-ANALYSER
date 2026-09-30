import pytest
from app.bullet_linter import audit_single_bullet_typography, audit_bullet_list_typography

def test_audit_single_bullet_clean():
    res = audit_single_bullet_typography("Architected microservices reducing latency by 40%.")
    assert not res["has_issues"]
    assert len(res["issues"]) == 0
    assert res["has_trailing_period"] is True

def test_audit_single_bullet_with_typos_and_spaces():
    bullet = "Acting product manger for teh team,collaborated with engineers (missing bracket."
    res = audit_single_bullet_typography(bullet)
    assert res["has_issues"] is True
    assert any("manger" in issue for issue in res["issues"])
    assert any("teh" in issue for issue in res["issues"])
    assert any("comma" in issue.lower() for issue in res["issues"])
    assert any("parentheses" in issue.lower() for issue in res["issues"])
    assert "manager" in res["suggested_bullet"]
    assert "the" in res["suggested_bullet"]

def test_audit_bullet_list_inconsistent_periods():
    bullets = [
        "Architected real-time streaming pipeline processing 10M events daily.",
        "Led team of 5 engineers delivering high-throughput microservices",
        "Optimized database queries resulting in 50% lower I/O cost."
    ]
    res = audit_bullet_list_typography(bullets)
    assert res["total_bullets"] == 3
    assert res["period_consistency"] == "Inconsistent"
    assert res["period_style"] == "Mixed"
    assert len(res["overall_alerts"]) > 0

def test_audit_bullet_list_consistent():
    bullets = [
        "Architected real-time streaming pipeline processing 10M events daily.",
        "Led team of 5 engineers delivering high-throughput microservices.",
        "Optimized database queries resulting in 50% lower I/O cost."
    ]
    res = audit_bullet_list_typography(bullets)
    assert res["period_consistency"] == "Consistent"
    assert res["period_style"] == "All Periods"
    assert res["cleanliness_score"] == 100

def test_bullet_typography_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.post("/api/audit/bullet-typography", json={
        "bullets": [
            "Architected real-time streaming pipeline processing 10M events daily.",
            "Led team of 5 engineers delivering high-throughput microservices."
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["cleanliness_score"] == 100
    assert data["period_consistency"] == "Consistent"

