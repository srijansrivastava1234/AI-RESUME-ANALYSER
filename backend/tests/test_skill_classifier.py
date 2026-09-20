"""
Unit test suite for hard vs soft skill taxonomy classifier and buzzword dilution detector.
"""

import pytest
from app.skill_classifier import (
    classify_single_skill,
    audit_skills,
    HARD_SKILL_TAXONOMY,
    SOFT_SKILL_BUZZWORDS,
)


def test_classify_single_skill_hard():
    cls_py = classify_single_skill("Python")
    assert cls_py["type"] == "HARD"
    assert cls_py["category"] == "Language"
    assert cls_py["is_buzzword"] is False

    cls_k8s = classify_single_skill("Kubernetes")
    assert cls_k8s["type"] == "HARD"
    assert cls_k8s["category"] == "Cloud/DevOps"

    cls_pg = classify_single_skill("PostgreSQL")
    assert cls_pg["type"] == "HARD"
    assert cls_pg["category"] == "Database"


def test_classify_single_skill_soft():
    cls_tp = classify_single_skill("team player")
    assert cls_tp["type"] == "SOFT"
    assert cls_tp["category"] == "Collaboration"
    assert cls_tp["is_buzzword"] is True

    cls_comm = classify_single_skill("strong communication")
    assert cls_comm["type"] == "SOFT"
    assert cls_comm["category"] == "Interpersonal"


def test_audit_skills_balanced_inventory():
    skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS", "Git"]
    result = audit_skills(skills)

    assert result["total_skills"] == 6
    assert result["hard_skills_count"] == 6
    assert result["soft_skills_count"] == 0
    assert result["hard_ratio"] == 100.0
    assert result["credibility_index"] == 100.0
    assert result["status"] == "EXCELLENT"
    assert len(result["warnings"]) == 0


def test_audit_skills_buzzword_dilution_warning():
    skills = [
        "Python", "Docker",
        "Team Player", "Strong Communication", "Fast Learner", "Passionate", "Self-starter"
    ]
    result = audit_skills(skills)

    assert result["hard_skills_count"] == 2
    assert result["soft_skills_count"] == 5
    assert result["soft_ratio"] > 50.0
    assert result["credibility_index"] < 80.0
    assert any("dilution" in w.lower() for w in result["warnings"])


def test_audit_skills_substantiation_in_experience():
    skills = ["Python", "Docker", "Kubernetes", "Redis", "Terraform"]
    experience_bullets = (
        "Engineered scalable backend microservices using Python and Docker. "
        "Integrated Redis caching layer reducing database queries by 45%."
    )
    result = audit_skills(skills, experience_text=experience_bullets)

    assert result["substantiation_rate"] == 60.0  # 3 of 5 substantiated
    assert "Python" in result["substantiated_skills"]
    assert "Docker" in result["substantiated_skills"]
    assert "Redis" in result["substantiated_skills"]
    assert "Kubernetes" in result["unsubstantiated_skills"]
    assert "Terraform" in result["unsubstantiated_skills"]
    assert any("unsubstantiated" in w.lower() for w in result["warnings"])


def test_audit_skills_empty_and_deduplication():
    res_empty = audit_skills([])
    assert res_empty["total_skills"] == 0
    assert res_empty["hard_skills_count"] == 0

    # Test deduplication
    skills_dup = ["Python", "python", "  Python  ", "Docker"]
    res_dup = audit_skills(skills_dup)
    assert res_dup["total_skills"] == 2


def test_partial_regex_matching():
    cls = classify_single_skill("Experienced in React.js development")
    assert cls["type"] == "HARD"
    assert cls["category"] == "Framework"

    cls_soft = classify_single_skill("Proven leadership in cross-functional teams")
    assert cls_soft["type"] == "SOFT"


def test_credibility_index_status_tiers():
    # Excellent
    assert audit_skills(["Go", "Rust", "Linux"])["status"] == "EXCELLENT"

    # Diluted
    heavily_diluted = ["Python", "Team player", "Self motivated", "Hard worker", "Detail oriented", "Go-getter"]
    assert audit_skills(heavily_diluted)["status"] == "DILUTED"
