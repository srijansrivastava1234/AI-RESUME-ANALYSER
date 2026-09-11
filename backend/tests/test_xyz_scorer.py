import pytest
from app.xyz_scorer import score_resume_bullet

class TestXYZScorer:
    def test_score_resume_bullet_elite_xyz(self):
        bullet = "Spearheaded migration of legacy monolith to FastAPI microservices on AWS, reducing p99 latency by 45% and saving $120k annually."
        result = score_resume_bullet(bullet)
        assert result["score"] >= 85
        assert result["tier"] == "Elite XYZ Impact"
        assert "Spearheaded" in result["detected_action_verbs"]
        assert any("45%" in m for m in result["detected_metrics"])
        assert any("fastapi" in t.lower() for t in result["detected_tools"])
        assert len(result["penalties"]) == 0

    def test_score_resume_bullet_passive_duty_penalty(self):
        bullet = "Responsible for assisting the development team with regular bug fixes and software updates."
        result = score_resume_bullet(bullet)
        assert result["score"] < 50
        assert result["tier"] == "Weak / Passive Phrasing"
        duty_penalties = [p for p in result["penalties"] if p["name"] == "Passive Duty Statement"]
        assert len(duty_penalties) == 1
        assert duty_penalties[0]["deduction"] == 40
        assert any("Replace passive duty statements" in tip for tip in result["improvement_tips"])

    def test_score_resume_bullet_missing_metrics(self):
        bullet = "Engineered backend microservices using Python and PostgreSQL."
        result = score_resume_bullet(bullet)
        assert result["component_scores"]["metric_score"] == 10
        assert any("Incorporate quantifiable metrics" in tip for tip in result["improvement_tips"])

    def test_score_resume_bullet_excessive_length_penalty(self):
        long_bullet = (
            "Architected and deployed a multi-region distributed streaming pipeline using Apache Kafka, "
            "Docker, and Kubernetes while collaborating closely with product managers and multiple cross-functional "
            "stakeholders to ensure high uptime and continuous reliability across twenty enterprise client platforms "
            "delivering strong results every single business quarter."
        )
        result = score_resume_bullet(long_bullet)
        length_penalties = [p for p in result["penalties"] if p["name"] == "Cognitive Overload / Verbosity"]
        assert len(length_penalties) == 1
        assert length_penalties[0]["deduction"] == 25

    def test_score_resume_bullet_under_detailed_penalty(self):
        short_bullet = "Fixed bugs in code."
        result = score_resume_bullet(short_bullet)
        assert result["word_count"] < 6
        short_penalties = [p for p in result["penalties"] if p["name"] == "Under-Detailed Statement"]
        assert len(short_penalties) == 1
        assert short_penalties[0]["deduction"] == 30

    def test_score_resume_bullet_empty_input(self):
        result = score_resume_bullet("   \n\t  ")
        assert result["score"] == 0
        assert result["tier"] == "Empty"
        assert result["component_scores"]["action_score"] == 0

    def test_score_resume_bullet_medium_verbs(self):
        bullet = "Built RESTful APIs in Node.js serving 10000+ users."
        result = score_resume_bullet(bullet)
        assert result["component_scores"]["action_score"] == 75
        assert "Built" in result["detected_action_verbs"]
        assert result["score"] >= 65

    def test_score_resume_bullet_currency_and_latency_metrics(self):
        bullet = "Optimized database queries with Redis caching, cutting latency to 15ms and reducing server costs by $30k."
        result = score_resume_bullet(bullet)
        assert result["score"] >= 85
        assert result["component_scores"]["metric_score"] == 100
        assert any("$30k" in m or "$30" in m for m in result["detected_metrics"])
