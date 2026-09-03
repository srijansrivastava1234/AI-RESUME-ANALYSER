import pytest
from app.analyzer import analyze_resume

def test_analyze_resume_heuristic_fallback():
    resume_text = """
    Jane Doe
    Software Engineer with expertise in Python, React, FastAPI, Docker, and PostgreSQL.
    Developed scalable microservices reducing API latency by 40%.
    Architected CI/CD deployment pipelines using GitHub Actions.
    """
    job_desc = "Looking for a Python and FastAPI developer with Docker and cloud experience."
    
    # Run analysis without relying on external Gemini API
    result = analyze_resume(resume_text, job_desc)
    
    assert "score" in result
    assert 0 <= result["score"] <= 100
    assert "breakdown" in result
    assert "skills" in result
    assert isinstance(result["skills"], list)
    assert len(result["skills"]) > 0
    assert "feedback" in result
