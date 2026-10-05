import pytest
from backend.app.simulators.lever import simulate_lever_parsing

def test_simulate_lever_empty_input():
    res = simulate_lever_parsing("")
    assert res["compatibility_score"] == 0
    assert res["is_safe"] is False
    assert "Empty document provided." in res["hazards"]

def test_simulate_lever_ideal_resume():
    text = """
    Jane Doe
    jane.doe@example.com | (555) 123-4567 | San Francisco, CA
    
    Professional Summary
    Senior Software Engineer with 7+ years of experience architecting scalable distributed systems.
    
    Experience
    Senior Backend Architect - Tech Corp (2020 - Present)
    • Architected and deployed microservices using Python and FastAPI, reducing latency by 45%.
    • Engineered distributed caching layer with Redis and PostgreSQL handling 50k requests per second.
    • Led team of 6 engineers to build React and TypeScript frontend interfaces for analytics dashboards.
    • Optimized AWS Kubernetes clusters, cutting cloud infrastructure costs by $120,000 annually.
    
    Skills
    Python, FastAPI, TypeScript, React, Docker, Kubernetes, AWS, PostgreSQL, Redis
    """
    res = simulate_lever_parsing(text)
    assert res["engine"] == "Lever"
    assert res["compatibility_score"] >= 75
    assert res["is_safe"] is True
    assert "Senior" in res["extracted_entities"]["fast_tags"]
    assert "Python" in res["extracted_entities"]["fast_tags"]
    assert "React/Frontend" in res["extracted_entities"]["fast_tags"]
    assert res["extracted_entities"]["has_contact_info"] is True
    assert res["extracted_entities"]["proximity_score"] > 50

def test_simulate_lever_table_and_missing_contact():
    text = """
    | Skill | Level | Years |
    | Python | Expert | 5 |
    | Docker | Advanced | 3 |
    | AWS | Intermediate | 2 |
    | React | Expert | 4 |
    | SQL | Expert | 6 |
    | Redis | Intermediate | 2 |
    | Node | Beginner | 1 |
    
    Experience
    Worked on several projects with Python, Docker, AWS, React, SQL, Redis, and Node.
    """
    res = simulate_lever_parsing(text)
    assert res["compatibility_score"] < 75
    assert res["is_safe"] is False
    assert any("pipe table separators" in h for h in res["hazards"])
    assert any("Missing or unparseable email" in h for h in res["hazards"])
