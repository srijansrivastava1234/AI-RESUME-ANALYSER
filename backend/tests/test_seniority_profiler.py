import pytest
from app.seniority_profiler import (
    audit_seniority_distribution,
    SENIORITY_PROFILES,
    STRATEGIC_KEYWORDS
)

class TestSeniorityProfiler:
    def test_empty_bullets_handling(self):
        result = audit_seniority_distribution([], target_tier="senior")
        assert result["total_bullets"] == 0
        assert result["seniority_alignment_index"] == 0
        assert result["alignment_grade"] == "D"
        assert result["actual_xyz_ratio"] == 0.0
        assert len(result["recommendations"]) >= 1

    def test_senior_tier_high_xyz_alignment(self):
        bullets = [
            "Architected distributed event streaming pipeline using Kafka reducing latency by 45%.",
            "Engineered automated CI/CD deployment pipeline with GitHub Actions saving 12 hours weekly.",
            "Optimized PostgreSQL database query indexes improving p99 response times by 35%.",
            "Modernized microservices architecture with Kubernetes achieving 99.99% system availability.",
            "Spearheaded architectural roadmap across 3 cross-functional teams."
        ]
        result = audit_seniority_distribution(bullets, target_tier="senior")
        assert result["total_bullets"] == 5
        assert result["quantified_count"] >= 4
        assert result["actual_xyz_ratio"] >= 0.80
        assert result["seniority_alignment_index"] >= 85
        assert result["alignment_grade"] in ("A", "A+")
        assert result["duty_count"] == 0

    def test_junior_tier_velocity_profile(self):
        bullets = [
            "Implemented REST API endpoints with FastAPI and Python resolving 25+ bug tickets.",
            "Constructed React UI component library increasing code reusability across 4 modules.",
            "Developed automated unit test suite with Pytest achieving 85% code coverage.",
            "Assisted team with daily sprint ceremonies and documentation updates."
        ]
        result = audit_seniority_distribution(bullets, target_tier="junior")
        assert result["total_bullets"] == 4
        assert result["target_tier"] == "junior"
        assert result["target_xyz_ratio"] == 0.70
        assert result["actual_xyz_ratio"] >= 0.50
        assert result["seniority_alignment_index"] >= 60

    def test_staff_tier_strategic_leadership_balance(self):
        bullets = [
            "Architected cloud infrastructure migration to AWS reducing compute costs by $180k annually.",
            "Formulated cross-org technical standards and governance charter adopted by 6 engineering squads.",
            "Spearheaded architectural roadmap and mentored 8 senior engineers toward principal promotions.",
            "Optimized core transaction processing engine handling 50,000 req/s with zero downtime.",
            "Standardized enterprise API gateway specifications aligning stakeholders across product lines."
        ]
        result = audit_seniority_distribution(bullets, target_tier="staff")
        assert result["total_bullets"] == 5
        assert result["target_tier"] == "staff"
        assert result["target_strategic_ratio"] == 0.40
        assert result["strategic_count"] >= 2
        assert result["seniority_alignment_index"] >= 80

    def test_passive_duty_phrasing_penalty(self):
        bullets = [
            "Responsible for monitoring system logs and reporting bugs.",
            "Assisted in backend development and helped with database migrations.",
            "Worked on fixing UI issues in the web application."
        ]
        result = audit_seniority_distribution(bullets, target_tier="mid")
        assert result["duty_count"] >= 2
        assert result["duty_ratio"] > 0.5
        assert result["seniority_alignment_index"] < 65
        assert any("passive phrasing" in rec.lower() for rec in result["recommendations"])

    def test_under_indexing_on_metrics_recommendation(self):
        bullets = [
            "Maintained backend services and updated API documentation.",
            "Built features using React and TypeScript for frontend dashboard.",
            "Coordinated with QA engineers for release testing."
        ]
        result = audit_seniority_distribution(bullets, target_tier="senior")
        assert result["actual_xyz_ratio"] == 0.0
        assert any("under-indexing on quantifiable metrics" in rec.lower() for rec in result["recommendations"])

    def test_unknown_tier_defaults_to_senior(self):
        bullets = [
            "Engineered Redis caching layer decreasing API latency by 60%."
        ]
        result = audit_seniority_distribution(bullets, target_tier="architect_overlord")
        assert result["target_xyz_ratio"] == SENIORITY_PROFILES["senior"]["target_xyz_ratio"]
        assert result["tier_title"] == SENIORITY_PROFILES["senior"]["title"]

    def test_case_insensitivity_and_whitespace(self):
        bullets = [
            "Pioneered enterprise risk mitigation framework and managed $2.5M departmental budget.",
            "Spearheaded organizational transformation and governance model across 12 departments."
        ]
        result = audit_seniority_distribution(bullets, target_tier="  EXECUTIVE  ")
        assert result["target_tier"] == "executive"
        assert result["target_xyz_ratio"] == 0.50
        assert result["strategic_count"] >= 1
