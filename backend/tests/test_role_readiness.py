import pytest
from app.role_readiness import evaluate_role_readiness, ROLE_ARCHETYPES

def test_empty_resume():
    res = evaluate_role_readiness("")
    assert res["readiness_score"] == 0.0
    assert res["readiness_tier"] == "Pivot Required"
    assert len(res["recommendations"]) > 0

def test_backend_readiness_strong():
    resume = """
    Senior Backend Engineer with 6 years of experience.
    Proficient in Python, Go, FastAPI, Django, SQL, PostgreSQL, REST APIs, and microservices architecture.
    Hands-on expertise with Docker, Kubernetes, Redis, AWS, and CI/CD pipelines.
    """
    res = evaluate_role_readiness(resume, target_role="backend_engineer")
    assert res["target_role"] == "backend_engineer"
    assert res["readiness_score"] >= 90.0
    assert res["readiness_tier"] == "Ready"
    assert "python" in res["matched_skills"]
    assert "fastapi" in res["matched_skills"]
    assert "postgresql" in res["matched_skills"]
    assert "docker" in res["matched_skills"]

def test_frontend_readiness():
    resume = """
    Frontend Developer experienced in JavaScript, TypeScript, HTML, CSS, React, Next.js, and Tailwind CSS.
    Built scalable UI with Redux, Vite, and Jest test automation.
    """
    res = evaluate_role_readiness(resume, target_role="frontend_engineer")
    assert res["target_role"] == "frontend_engineer"
    assert res["readiness_score"] >= 90.0
    assert res["readiness_tier"] == "Ready"
    assert "react" in res["matched_skills"]
    assert "typescript" in res["matched_skills"]

def test_automatic_archetype_inference():
    resume = """
    Machine Learning Specialist proficient in Python, PyTorch, TensorFlow, Scikit-learn, Deep Learning, Pandas, NumPy, SQL.
    Deployed LLM models, LangChain, Transformers, and MLOps on AWS with Docker.
    """
    res = evaluate_role_readiness(resume)  # target_role is None
    assert res["target_role"] == "ml_engineer"
    assert res["readiness_score"] >= 90.0
    assert res["all_role_scores"]["ml_engineer"] > res["all_role_scores"]["frontend_engineer"]
