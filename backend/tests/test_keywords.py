import pytest
from app.keywords import extract_skills_by_category, calculate_keyword_match_score

def test_extract_skills_by_category():
    sample_text = """
    Experienced Full Stack Engineer skilled in Python, TypeScript, React, and FastAPI.
    Proficient with Docker, Kubernetes, PostgreSQL, Redis, and Microservices architecture.
    Practiced in Agile and Unit Testing.
    """
    categorized = extract_skills_by_category(sample_text)
    
    assert "Languages" in categorized
    assert any("Python" in s for s in categorized["Languages"])
    
    assert "Frameworks & Libraries" in categorized
    assert any("React" in s for s in categorized["Frameworks & Libraries"])
    assert any("Fastapi" in s or "FastAPI" in s.upper() for s in categorized["Frameworks & Libraries"])
    
    assert "Cloud & DevOps" in categorized
    assert any("Docker" in s for s in categorized["Cloud & DevOps"])
    
    assert "Databases & Storage" in categorized
    assert any("Postgresql" in s or "POSTGRESQL" in s.upper() for s in categorized["Databases & Storage"])

def test_calculate_keyword_match_score():
    resume = "Python, FastAPI, Docker, PostgreSQL, React"
    job = "We are hiring for Python, FastAPI, Docker, Kubernetes, and AWS."
    
    result = calculate_keyword_match_score(resume, job)
    assert result["match_percentage"] > 0
    assert len(result["matched_keywords"]) > 0
    assert len(result["missing_keywords"]) > 0
    assert any("Kubernetes" in k for k in result["missing_keywords"])

def test_calculate_keyword_match_empty_job():
    resume = "Python, React, Docker"
    result = calculate_keyword_match_score(resume, "")
    assert result["match_percentage"] == 100
