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


def test_hygiene_endpoint_valid_txt():
    sample_text = (
        "Alice Smith\n"
        "alice@example.com | (555) 019-2834 | linkedin.com/in/alicesmith\n"
        "EXPERIENCE\n"
        "- Built high-throughput backend services in Python.\n"
        "- Designed distributed caches with Redis.\n"
        "- Automated testing pipeline with 90% coverage.\n"
        "EDUCATION\n"
        "B.S. in Computer Engineering\n"
        "SKILLS\n"
        "Python, FastAPI, Docker, Kubernetes, PostgreSQL\n"
        "PROJECTS\n"
        "Distributed Event Broker in Go and Kafka\n"
    )
    files = {"file": ("alice_resume.txt", io.BytesIO(sample_text.encode("utf-8")), "text/plain")}
    response = client.post("/api/hygiene", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "alice_resume.txt"
    assert "hygiene" in data
    assert data["hygiene"]["hygiene_score"] >= 80
    assert data["hygiene"]["contacts"]["email"] == "alice@example.com"
    assert len(data["hygiene"]["checklist"]) > 5


def test_analyze_endpoint_includes_formatting_hygiene():
    sample_resume = (
        "Jane Doe\n"
        "jane.doe@example.com | (555) 123-4567\n"
        "Software Engineer\n"
        "Skills: Python, FastAPI, Docker, React, PostgreSQL\n"
        "Experience:\n"
        "- Developed high throughput APIs improving latency by 30%.\n"
        "- Led containerization migration to Docker Swarm.\n"
        "- Implemented unit testing reducing defect rate by 40%.\n"
        "Education: B.S. Computer Science\n"
    )
    files = {"file": ("resume.txt", io.BytesIO(sample_resume.encode("utf-8")), "text/plain")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert "formatting_hygiene" in res_data["report"]
    assert res_data["report"]["formatting_hygiene"]["hygiene_score"] > 50


def test_score_bullet_endpoint_elite():
    payload = {
        "bullet": "Spearheaded migration of legacy monolith to FastAPI microservices on AWS, reducing p99 latency by 45% and saving $120k annually.",
        "seniority": "senior"
    }
    response = client.post("/api/score-bullet", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= 85
    assert data["tier"] == "Elite XYZ Impact"
    assert "Spearheaded" in data["detected_action_verbs"]
    assert any("45%" in m for m in data["detected_metrics"])
    assert any("fastapi" in t.lower() for t in data["detected_tools"])


def test_score_bullet_endpoint_passive_penalty():
    payload = {
        "bullet": "Responsible for assisting the development team with regular bug fixes and software updates.",
        "seniority": "mid"
    }
    response = client.post("/api/score-bullet", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["score"] < 50
    assert data["tier"] == "Weak / Passive Phrasing"
    duty_penalties = [p for p in data["penalties"] if p["name"] == "Passive Duty Statement"]
    assert len(duty_penalties) == 1
    assert duty_penalties[0]["deduction"] == 40


def test_score_bullet_endpoint_seniority_levels():
    bullet = "Built microservices using Python and PostgreSQL."
    for level in ["junior", "mid", "senior", "staff"]:
        res = client.post("/api/score-bullet", json={"bullet": bullet, "seniority": level})
        assert res.status_code == 200
        assert "score" in res.json()


def test_score_bullet_endpoint_empty_and_short():
    res = client.post("/api/score-bullet", json={"bullet": "   ", "seniority": "mid"})
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 0
    assert data["tier"] == "Empty"


def test_verb_diversity_endpoint_success():
    payload = {
        "bullets": [
            "Architected low-latency microservices with FastAPI and Kafka.",
            "Engineered automated CI/CD pipeline cutting deployment times by 40%.",
            "Spearheaded database indexing in PostgreSQL to reduce query latency.",
            "Optimized memory usage in Go microservices."
        ]
    }
    res = client.post("/api/verb-diversity", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "diversity_score" in data
    assert data["diversity_score"] >= 80
    assert data["total_verbs_found"] >= 4
    assert len(data["repetition_warnings"]) == 0


def test_verb_diversity_endpoint_empty_list():
    res = client.post("/api/verb-diversity", json={"bullets": []})
    assert res.status_code == 422  # Pydantic min_items=1 validation error


def test_viewport_audit_endpoint():
    payload = {
        "resume_text": "Architected cloud services with AWS. Reduced latency by 45% using Redis caching.",
        "target_skills": ["AWS", "Redis"]
    }
    res = client.post("/api/viewport-audit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "viewport_precision_score" in data
    assert "status" in data
    assert "recommendations" in data


def test_expand_keywords_endpoint():
    payload = {
        "text": "Senior Engineer experienced with K8s, AWS, and TypeScript."
    }
    res = client.post("/api/expand-keywords", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "detected_terms" in data
    assert "expansions" in data
    assert len(data["detected_terms"]) > 0


def test_adverse_impact_endpoint():
    payload = {
        "group_data": {
            "Group_A": {"total": 100, "selected": 60},
            "Group_B": {"total": 80, "selected": 52}
        }
    }
    res = client.post("/api/adverse-impact", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "is_compliant" in data
    assert data["is_compliant"] is True
    assert "benchmark_group" in data
    assert data["status"] == "COMPLIANT_SAFE_HARBOR"


def test_detect_hacks_endpoint_clean():
    payload = {
        "text": "Jane Doe. Experienced Software Engineer in Python and Docker."
    }
    res = client.post("/api/detect-hacks", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["hack_risk_score"] == 100
    assert data["disqualification_risk"] == "None"
    assert data["clean_text_certified"] is True


def test_detect_hacks_endpoint_spam():
    payload = {
        "text": "Jane Doe",
        "raw_markup": "<div style='color: #ffffff; opacity: 0;'>hidden keyword dump</div>"
    }
    res = client.post("/api/detect-hacks", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_flagged"] is True
    assert data["clean_text_certified"] is False
    assert len(data["detected_traps"]) > 0


def test_audit_headers_endpoint():
    payload = {
        "resume_text": "Professional Experience\nSenior Dev\nEducation\nBS CS\nTechnical Skills\nPython"
    }
    res = client.post("/api/audit-headers", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["canonical_score"] == 100
    assert "found_canonicals" in data
    assert "Skills" in data["found_canonicals"]


def test_token_density_endpoint():
    payload = {
        "text": "Architected event-driven microservices using Python and FastAPI. Reduced latency by 45%."
    }
    res = client.post("/api/token-density", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "signal_to_noise_ratio" in data
    assert "type_token_ratio" in data
    assert data["verdict"] == "Optimal Technical Density"


def test_validate_metric_endpoint():
    # True business outcome
    res_outcome = client.post("/api/validate-metric", json={"bullet": "Cut infrastructure costs by $120K annually."})
    assert res_outcome.status_code == 200
    data_outcome = res_outcome.json()
    assert data_outcome["has_business_outcome"] is True
    assert data_outcome["vanity_penalty"] == 0

    # Vanity activity
    res_vanity = client.post("/api/validate-metric", json={"bullet": "Wrote 8,000 lines of code across features."})
    assert res_vanity.status_code == 200
    data_vanity = res_vanity.json()
    assert data_vanity["has_vanity_metric"] is True
def test_seniority_profile_endpoint_success():
    payload = {
        "bullets": [
            "Architected Kafka event pipeline reducing message latency by 35%.",
            "Deployed microservices on Kubernetes cluster saving 15 hours weekly.",
            "Formulated cross-org technical standards and mentored 5 engineers."
        ],
        "target_tier": "staff"
    }
    res = client.post("/api/seniority-profile", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["target_tier"] == "staff"
    assert "seniority_alignment_index" in data
    assert "target_xyz_ratio" in data
    assert "actual_xyz_ratio" in data
    assert data["total_bullets"] == 3


def test_seniority_profile_endpoint_default_tier():
    payload = {
        "bullets": ["Implemented REST endpoints in FastAPI."]
    }
    res = client.post("/api/seniority-profile", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["target_tier"] == "senior"
    assert data["total_bullets"] == 1


def test_redact_pii_endpoint_success():
    payload = {
        "text": "Alice Engineer\nEmail: alice@work.com | Phone: 555-019-2831\nLinkedIn: https://linkedin.com/in/alice-dev\nGraduated 2014 from MIT with BS Computer Science."
    }
    res = client.post("/api/redact-pii", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["safe_harbor_certified"] is True
    assert data["total_redactions"] >= 3
    assert "[EMAIL REDACTED]" in data["sanitized_text"]
    assert "[PHONE REDACTED]" in data["sanitized_text"]
    assert "[GRADUATION YEAR REDACTED - AGE PROXY DEFENSE]" in data["sanitized_text"]
    assert "alice@work.com" not in data["sanitized_text"]


def test_redact_pii_endpoint_empty():
    res = client.post("/api/redact-pii", json={"text": ""})
    assert res.status_code == 422  # min_length=1 validation error







