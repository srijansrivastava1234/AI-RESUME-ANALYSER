import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Online"
    assert "version" in data
    assert "endpoints" in data

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "supported_formats" in data
    assert "pdf" in data["supported_formats"]
    assert "docx" in data["supported_formats"]
    assert "txt" in data["supported_formats"]

def test_security_and_timing_headers():
    response = client.get("/api/health")
    assert "X-Process-Time" in response.headers
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"

def test_analyze_endpoint_with_txt_file():
    sample_resume = (
        "Jane Doe\n"
        "Software Engineer\n"
        "Skills: Python, FastAPI, Docker, React, PostgreSQL\n"
        "Experience:\n"
        "Developed high throughput APIs improving latency by 30%.\n"
        "Education: B.S. Computer Science\n"
    )
    files = {
        "file": ("resume.txt", io.BytesIO(sample_resume.encode("utf-8")), "text/plain")
    }
    data = {
        "job_description": "We are seeking a Python engineer proficient in FastAPI and Docker."
    }
    
    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["filename"] == "resume.txt"
    assert res_data["char_count"] > 0
    assert "report" in res_data
    assert "ats_score" in res_data["report"]
    assert "metrics" in res_data["report"]
    assert "keywords" in res_data["report"]

def test_analyze_endpoint_invalid_file_extension():
    files = {
        "file": ("script.exe", io.BytesIO(b"binary data"), "application/octet-stream")
    }
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]

def test_analyze_endpoint_missing_file():
    response = client.post("/api/analyze")
    assert response.status_code == 422

def test_optimize_bullet_endpoint_valid():
    payload = {
        "bullet": "helped maintain customer database and fixed frontend bugs",
        "target_role": "Backend Engineer"
    }
    response = client.post("/api/optimize-bullet", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "original" in data
    assert "optimized" in data
    assert "action_verb_used" in data
    assert "framework" in data
    assert "feedback" in data

def test_optimize_bullet_endpoint_too_short():
    payload = {
        "bullet": "fix"
    }
    response = client.post("/api/optimize-bullet", json=payload)
    assert response.status_code == 422  # validation error for min_length=5


def test_compare_endpoint_valid_resumes():
    file1 = ("alice.txt", io.BytesIO(b"Alice Senior Engineer. Skills: Python, FastAPI, Docker."), "text/plain")
    file2 = ("bob.txt", io.BytesIO(b"Bob Junior Developer. Skills: HTML, CSS."), "text/plain")

    response = client.post(
        "/api/compare",
        files=[("files", file1), ("files", file2)],
        data={"job_description": "Senior Python Engineer with FastAPI"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_compared"] == 2
    assert len(data["rankings"]) == 2
    assert "summary" in data
    assert data["rankings"][0]["rank"] == 1


def test_compare_endpoint_fewer_than_two_resumes_rejected():
    file1 = ("single.txt", io.BytesIO(b"Only one candidate"), "text/plain")
    response = client.post(
        "/api/compare",
        files=[("files", file1)]
    )
    assert response.status_code == 400
    assert "At least 2 resume files are required" in response.json()["detail"]


def test_compare_endpoint_invalid_extension():
    file1 = ("doc.pdf", io.BytesIO(b"%PDF-1.4 mock"), "application/pdf")
    file2 = ("evil.exe", io.BytesIO(b"binary"), "application/octet-stream")
    response = client.post(
        "/api/compare",
        files=[("files", file1), ("files", file2)]
    )
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]


def test_rate_limiter_configured_on_app():
    assert hasattr(app.state, "limiter")
    assert app.state.limiter is not None

