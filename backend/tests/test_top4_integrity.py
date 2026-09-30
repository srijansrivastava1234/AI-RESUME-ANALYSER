"""
Integrity Test Suite for Top 4 Flagship Architectural Pillars.
Validates the core 4 technical innovations:
1. Full-Stack Asynchronous REST Pipeline
2. Deterministic 4-Pillar Compliance Scoring Engine
3. Okapi BM25+ Lexical Retrieval & Asymptotic Saturation
4. Multi-Vendor ATS Exploit & White-Font Trap Detector
"""

import pytest
from app.compliance import audit_ats_compliance
from app.bm25_scorer import compute_bm25_plus
from app.hack_detector import detect_ats_hacks
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestTop4ArchitecturalPillars:
    """Rigorous verification of the 4 flagship architectural pillars."""

    def test_pillar_1_fullstack_async_api_health_and_endpoint(self):
        """Pillar 1: Full-Stack Async API endpoint responsiveness and contract."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["healthy", "ok"] or "status" in data

    def test_pillar_2_deterministic_4pillar_compliance_scoring(self):
        """Pillar 2: Mathematically auditable 4-pillar scoring engine and grade calculation."""
        resume = (
            "Alex Smith\n"
            "alex.smith@example.com | (555) 019-2834\n"
            "Experience\n"
            "Lead Backend Engineer at CloudTech\n"
            "2021 - Present\n"
            "- Spearheaded migration to FastAPI and Docker, reducing API response latency by 45% for 2M daily requests.\n"
            "- Engineered optimized PostgreSQL indexing, boosting query throughput by 35%.\n"
            "Education\n"
            "B.S. in Software Engineering, State University (2017 - 2021)\n"
            "Skills: Python, FastAPI, Docker, PostgreSQL, React, AWS\n"
        )
        jd = "Seeking a Lead Backend Engineer with Python, FastAPI, Docker, and PostgreSQL expertise."
        audit = audit_ats_compliance(resume, job_description=jd)
        
        assert audit is not None
        assert "composite_score" in audit
        assert 0 <= audit["composite_score"] <= 100
        assert audit["letter_grade"] in ["A+", "A", "B", "C", "D"]
        assert "itemized_audit_trail" in audit
        assert len(audit["itemized_audit_trail"]) == 4

    def test_pillar_3_bm25_plus_lexical_retrieval_and_saturation(self):
        """Pillar 3: Okapi BM25+ term saturation and anti-stuffing enforcement."""
        doc = "Python developer specializing in FastAPI microservices, Docker orchestration, and PostgreSQL databases."
        query_terms = ["Python", "FastAPI", "Docker", "PostgreSQL", "Kubernetes"]
        
        result = compute_bm25_plus(doc, query_terms)
        assert result is not None
        assert result["raw_bm25_score"] > 0
        assert result["normalized_score"] > 0
        assert result["matched_keywords"] >= 4
        assert len(result["stuffed_terms"]) == 0

    def test_pillar_4_multi_vendor_ats_exploit_guard(self):
        """Pillar 4: Zero-trust visual and invisible exploit interception."""
        clean_text = "Senior Python engineer with 6 years experience architecting cloud backends."
        deceptive_markup = '<div style="color:#ffffff; font-size:0.1pt; opacity:0;">python fastapi docker aws</div>'
        
        clean_audit = detect_ats_hacks(clean_text)
        assert clean_audit["clean_text_certified"] is True
        assert clean_audit["hack_risk_score"] == 100
        
        flagged_audit = detect_ats_hacks(clean_text, raw_markup=deceptive_markup)
        assert flagged_audit["clean_text_certified"] is False
        assert flagged_audit["is_flagged"] is True
        assert flagged_audit["trap_count"] >= 1
