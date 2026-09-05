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
