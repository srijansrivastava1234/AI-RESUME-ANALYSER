"""
Unit tests for the multi-resume comparator engine (app.comparator).
Verifies ranking logic, score sorting, error boundaries, and summary generation.
"""

import pytest
from unittest.mock import patch
from app.comparator import compare_resumes


SAMPLE_RESUME_1 = {
    "filename": "alice_resume.pdf",
    "text": "Experienced Python Software Engineer with FastAPI, Docker, and AWS skills. Built scalable microservices."
}

SAMPLE_RESUME_2 = {
    "filename": "bob_resume.docx",
    "text": "Junior developer with basic Python knowledge. Looking for an internship in software development."
}

SAMPLE_RESUME_3 = {
    "filename": "charlie_resume.txt",
    "text": "Staff Architect specialized in Python, Kubernetes, distributed systems, and PostgreSQL."
}

JOB_DESCRIPTION = "Seeking a Senior Python Engineer skilled in FastAPI, AWS, Docker, and distributed systems."


class TestResumeComparator:
    """Test suite for compare_resumes function."""

    def test_compare_minimum_two_resumes_success(self):
        """Validates comparison of 2 valid resumes returns ranked results."""
        resumes = [SAMPLE_RESUME_1, SAMPLE_RESUME_2]
        report = compare_resumes(resumes, JOB_DESCRIPTION)

        assert report["total_compared"] == 2
        assert "rankings" in report
        assert len(report["rankings"]) == 2

        # Check rankings are sorted
        rankings = report["rankings"]
        assert rankings[0]["rank"] == 1
        assert rankings[1]["rank"] == 2
        assert rankings[0]["ats_score"] >= rankings[1]["ats_score"]

        # Check summary contains winner info
        assert "ranks #1" in report["summary"]

    def test_compare_three_resumes_correct_ranking_order(self):
        """Validates that 3 resumes are correctly sorted by ATS score descending."""
        resumes = [SAMPLE_RESUME_1, SAMPLE_RESUME_2, SAMPLE_RESUME_3]
        report = compare_resumes(resumes, JOB_DESCRIPTION)

        assert report["total_compared"] == 3
        scores = [r["ats_score"] for r in report["rankings"]]
        assert scores == sorted(scores, reverse=True)

    def test_compare_less_than_two_resumes_raises_value_error(self):
        """Ensures ValueError is raised when fewer than 2 resumes are provided."""
        with pytest.raises(ValueError, match="At least 2 resumes are required"):
            compare_resumes([SAMPLE_RESUME_1], JOB_DESCRIPTION)

        with pytest.raises(ValueError, match="At least 2 resumes are required"):
            compare_resumes([], JOB_DESCRIPTION)

    def test_compare_more_than_five_resumes_raises_value_error(self):
        """Ensures ValueError is raised when more than 5 resumes are provided."""
        six_resumes = [SAMPLE_RESUME_1] * 6
        with pytest.raises(ValueError, match="Maximum 5 resumes can be compared"):
            compare_resumes(six_resumes, JOB_DESCRIPTION)

    def test_compare_skips_empty_resumes(self):
        """Validates that resumes with empty text are skipped from comparison."""
        empty_resume = {"filename": "empty.pdf", "text": "   "}
        resumes = [SAMPLE_RESUME_1, SAMPLE_RESUME_2, empty_resume]
        report = compare_resumes(resumes, JOB_DESCRIPTION)

        assert report["total_compared"] == 2
        filenames = [r["filename"] for r in report["rankings"]]
        assert "empty.pdf" not in filenames

    def test_compare_without_job_description(self):
        """Validates comparison works without an explicit job description."""
        resumes = [SAMPLE_RESUME_1, SAMPLE_RESUME_2]
        report = compare_resumes(resumes, None)

        assert report["total_compared"] == 2
        assert report["rankings"][0]["ats_score"] >= 0
        assert "summary" in report
