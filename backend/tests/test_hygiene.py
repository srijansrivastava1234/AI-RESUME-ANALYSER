"""
Unit tests for the ATS formatting hygiene evaluator (app.hygiene).
Validates contact extraction, section heading detection, scoring logic, and checklist output.
"""

import pytest
from app.hygiene import audit_resume_hygiene, calculate_readability_metrics


WELL_FORMED_RESUME = """
Jane Doe
Email: jane.doe@example.com | Phone: (555) 123-4567 | linkedin.com/in/janedoe | github.com/janedoe

PROFESSIONAL SUMMARY
Results-driven Software Engineer with 5+ years of experience in distributed systems.

TECHNICAL SKILLS
- Languages: Python, JavaScript, TypeScript, Go
- Frameworks: FastAPI, React, Next.js, Node.js
- Cloud & DevOps: Docker, Kubernetes, AWS, CI/CD pipelines
- Databases: PostgreSQL, Redis, MongoDB

WORK EXPERIENCE
Senior Backend Engineer | TechCorp Inc. (2022 - Present)
- Designed and maintained high-throughput REST APIs handling 10M daily requests with 99.99% uptime.
- Optimized database queries using indexing and read-replicas, reducing p99 latency by 45%.
- Led a team of 4 engineers implementing automated CI/CD deployment pipelines on AWS.

Software Engineer | StartupLab (2020 - 2022)
- Built microservices using FastAPI and Docker for real-time data processing.
- Integrated third-party payment gateways and OAuth authentication flows.

PROJECTS
AI Resume Analyser
- Full-stack ATS audit engine built with FastAPI and React 19.
- Integrated Google Gemini 1.5 Flash for deterministic resume analysis.

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley (2016 - 2020)
"""

SPARSE_RESUME = """
Bob
Just looking for a job.
Did some coding in python.
"""


class TestResumeHygiene:
    """Test suite for audit_resume_hygiene function."""

    def test_well_formed_resume_high_hygiene_score(self):
        """Verifies that a well-structured resume receives a high hygiene score and Excellent rating."""
        report = audit_resume_hygiene(WELL_FORMED_RESUME)

        assert report["hygiene_score"] >= 85
        assert report["rating"] == "Excellent"
        assert report["word_count"] > 100
        assert report["bullet_count"] >= 3

        # Check contact detection
        assert report["contacts"]["email"] == "jane.doe@example.com"
        assert report["contacts"]["phone"] is not None
        assert report["contacts"]["linkedin"] == "janedoe"
        assert report["contacts"]["github"] == "janedoe"

        # Check section detection
        assert report["sections"]["experience"] is True
        assert report["sections"]["education"] is True
        assert report["sections"]["skills"] is True
        assert report["sections"]["projects"] is True
        assert len(report["missing_sections"]) == 0

        # Check checklist
        passed_items = [c for c in report["checklist"] if c["passed"]]
        assert len(passed_items) >= 7

    def test_sparse_resume_flags_missing_elements(self):
        """Verifies that a sparse resume triggers appropriate warnings and lower score."""
        report = audit_resume_hygiene(SPARSE_RESUME)

        assert report["hygiene_score"] < 60
        assert report["rating"] == "Needs Improvement"
        assert report["contacts"]["email"] is None
        assert report["contacts"]["phone"] is None

        # Check recommendations
        recs = " ".join(report["recommendations"]).lower()
        assert "email" in recs
        assert "phone" in recs
        assert "experience" in recs

    def test_empty_resume_raises_value_error(self):
        """Ensures ValueError is raised for blank input."""
        with pytest.raises(ValueError, match="cannot be empty"):
            audit_resume_hygiene("")

        with pytest.raises(ValueError, match="cannot be empty"):
            audit_resume_hygiene("   \n\t  ")

    def test_checklist_structure(self):
        """Verifies checklist items contain required schema fields."""
        report = audit_resume_hygiene(WELL_FORMED_RESUME)
        for item in report["checklist"]:
            assert "name" in item
            assert "passed" in item
            assert "status" in item
            assert "detail" in item

    def test_readability_metrics_included(self):
        """Verifies readability metrics are properly computed and returned in hygiene report."""
        report = audit_resume_hygiene(WELL_FORMED_RESUME)
        assert "readability" in report
        readability = report["readability"]
        assert "fk_grade_level" in readability
        assert "gunning_fog" in readability
        assert "reading_ease_tier" in readability
        assert 1.0 <= readability["fk_grade_level"] <= 20.0
        assert 1.0 <= readability["gunning_fog"] <= 20.0

    def test_calculate_readability_metrics_direct(self):
        """Verifies direct calculation of readability scores on standard prose."""
        sample_text = (
            "Architected high-throughput microservices using FastAPI and Kafka. "
            "Engineered zero-downtime deployment workflows on Kubernetes. "
            "Spearheaded database indexing in PostgreSQL to reduce query latency by 35%."
        )
        metrics = calculate_readability_metrics(sample_text)
        assert "fk_grade_level" in metrics
        assert metrics["reading_ease_tier"] in ["Optimal Technical Clarity", "Dense Executive Prose"]
        assert metrics["avg_sentence_length"] > 0

