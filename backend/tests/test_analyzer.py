import pytest
from app.analyzer import analyze_resume

def test_analyze_resume_heuristic_fallback():
    resume_text = """
    Jane Doe
    Software Engineer with expertise in Python, React, FastAPI, Docker, and PostgreSQL.
    Work Experience:
    Senior Developer at TechCorp (2021 - Present)
    - Developed scalable microservices reducing API latency by 40%.
    - Architected CI/CD deployment pipelines using GitHub Actions.
    Education:
    B.S. in Computer Science, State University, 2020
    Skills:
    Python, React, FastAPI, Docker, PostgreSQL, Git
    Projects:
    E-Commerce API with FastAPI and Redis caching.
    """
    job_desc = "Looking for a Python and FastAPI developer with Docker and cloud experience."
    
    # Run analysis without relying on external Gemini API
    result = analyze_resume(resume_text, job_desc)
    
    assert "ats_score" in result
    assert isinstance(result["ats_score"], int)
    assert 0 <= result["ats_score"] <= 100
    
    assert "metrics" in result
    assert isinstance(result["metrics"], list)
    assert len(result["metrics"]) >= 4
    
    assert "keywords" in result
    assert "detected" in result["keywords"]
    assert "missing" in result["keywords"]
    assert isinstance(result["keywords"]["detected"], list)
    assert len(result["keywords"]["detected"]) > 0
    
    assert "section_analysis" in result
    assert isinstance(result["section_analysis"], list)
    
    assert "key_strengths" in result
    assert isinstance(result["key_strengths"], list)
    
    assert "actionable_recommendations" in result
    assert isinstance(result["actionable_recommendations"], list)
    
    assert "job_compatibility" in result
    if result["job_compatibility"]:
        assert "score" in result["job_compatibility"]
        assert "skill_gaps" in result["job_compatibility"]
