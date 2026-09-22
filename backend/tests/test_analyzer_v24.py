import pytest
from app.analyzer import analyze_resume


def test_analyzer_integration_v24():
    sample_resume = """
    Jane Doe
    jane.doe@example.com | +1-555-0199 | https://linkedin.com/in/janedoe | https://github.com/janedoe
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 7+ years of experience specializing in distributed systems,
    cloud infrastructure, and microservices on AWS. Proven track record of scaling high-throughput APIs.
    
    WORK EXPERIENCE
    Senior Backend Engineer - CloudTech (2022 - Present)
    • Architected high-throughput microservices using FastAPI, Docker, and PostgreSQL, increasing system reliability by 35% across four cloud regions.
    • Spearheaded transition from legacy monolithic codebase to event-driven Kafka messaging, reducing backend data processing latency by 45 milliseconds.
    • Directed cross-functional engineering team of eight developers to deliver enterprise analytics features on time and under budget ($1.5M ARR).
    
    EDUCATION
    Bachelor of Science in Computer Science - State University
    
    SKILLS
    Python, FastAPI, Docker, Kubernetes, PostgreSQL, Kafka, Redis, AWS, Terraform, Git
    """
    
    result = analyze_resume(sample_resume)
    
    # Verify core ATS fields
    assert "ats_score" in result
    assert "keywords" in result
    assert "formatting_hygiene" in result
    
    # Verify v2.4.0 diagnostic suite integrations
    assert "readability" in result
    assert result["readability"]["flesch_reading_ease"] > 0
    
    assert "voice_analysis" in result
    assert result["voice_analysis"]["active_ratio_pct"] > 50.0
    
    assert "cliche_audit" in result
    assert result["cliche_audit"]["cleanliness_score"] > 80.0
    
    assert "metric_diversity" in result
    assert result["metric_diversity"]["diversity_score"] >= 40.0
    
    assert "skill_recency" in result
    assert result["skill_recency"]["is_active_career"] is True
    
    assert "bullet_lengths" in result
    assert result["bullet_lengths"]["total_bullets"] >= 3
    
    assert "summary_style" in result
    assert result["summary_style"]["style"] == "MODERN_VALUE_SUMMARY"
    
    assert "salary_disclosures" in result
    assert result["salary_disclosures"]["has_salary_disclosure"] is False
    
    assert "portfolio_links" in result
    assert result["portfolio_links"]["has_linkedin"] is True
    assert result["portfolio_links"]["has_github"] is True
