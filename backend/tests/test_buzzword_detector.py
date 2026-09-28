"""
Unit tests for buzzword_detector module.
"""

import pytest
from app.buzzword_detector import audit_buzzword_density, CORPORATE_BUZZWORDS


def test_empty_resume_buzzword_audit():
    result = audit_buzzword_density("")
    assert result["buzzword_count"] == 0
    assert result["buzzword_free_score"] == 100.0
    assert result["unique_buzzwords"] == []


def test_clean_resume_no_buzzwords():
    resume = (
        "Senior Backend Engineer with 8 years of experience in Python and Go. "
        "Architected distributed PostgreSQL clusters handling 50k RPS with 99.99% uptime. "
        "Reduced cloud infrastructure costs by 35% via Kubernetes autoscaling."
    )
    result = audit_buzzword_density(resume)
    assert result["buzzword_count"] == 0
    assert result["buzzword_free_score"] == 100.0
    assert "Excellent" in result["recommendations"][0]


def test_resume_with_heavy_buzzwords():
    resume = (
        "I am a results-driven rockstar developer and thought leader who creates synergy "
        "across cross-functional teams. A self-starter and team player with out of the box thinking."
    )
    result = audit_buzzword_density(resume)
    assert result["buzzword_count"] >= 5
    assert "rockstar" in result["unique_buzzwords"]
    assert "synergy" in result["unique_buzzwords"]
    assert "thought leader" in result["unique_buzzwords"]
    assert result["buzzword_free_score"] < 80.0
    assert len(result["detected_instances"]) >= 5
    assert "High buzzword density" in result["recommendations"][0]


def test_suggested_replacements_presence():
    resume = "Leveraged deep dive analytics to move the needle."
    result = audit_buzzword_density(resume)
    assert result["buzzword_count"] >= 2
    for inst in result["detected_instances"]:
        assert "suggested_replacement" in inst
        assert len(inst["suggested_replacement"]) > 0
