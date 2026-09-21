import pytest
from app.section_flow import audit_section_flow, detect_detected_section_order

def test_optimal_experienced_section_flow():
    sample = """John Doe
john@example.com

Summary
Seasoned full stack engineer with 6 years experience building scalable systems.

Work Experience
Senior Software Engineer at Acme Corp (2020 - Present)
- Engineered high-throughput microservices in Go and Python.

Skills
Python, FastAPI, Docker, Kubernetes, React, TypeScript

Projects
Open Source Resume Analyzer
- Built ATS parser with high accuracy.

Education
B.S. in Computer Science, State University (2016 - 2020)
"""
    result = audit_section_flow(sample, is_early_career=False)
    assert result["flow_score"] >= 90
    assert result["is_optimal"] is True
    assert "Work Experience" in result["detected_sequence"]
    assert "Skills" in result["detected_sequence"]
    assert "Education" in result["detected_sequence"]
    assert len(result["warnings"]) == 0

def test_suboptimal_flow_hobbies_before_experience():
    sample = """Jane Doe
jane@example.com

Hobbies
Gaming, Hiking, Chess

Work Experience
Frontend Developer at Beta LLC (2021 - Present)
- Developed responsive web interfaces.

Education
B.A. in Design
"""
    result = audit_section_flow(sample, is_early_career=False)
    assert result["flow_score"] < 75
    assert any("Hobbies" in w for w in result["warnings"])

def test_missing_experience_penalty():
    sample = """Alex Smith
alex@example.com

Education
B.S. in Physics

Skills
Python, Data Analysis
"""
    result = audit_section_flow(sample, is_early_career=False)
    assert result["flow_score"] < 70
    assert any("Work Experience" in w for w in result["warnings"])

def test_early_career_education_first():
    sample = """New Grad
grad@example.com

Summary
Aspiring software engineer graduating Spring 2024.

Education
B.S. Computer Science, Top Tech Institute (2020 - 2024)

Skills
Java, Python, C++, SQL

Projects
Distributed Key-Value Store
- Implemented Raft consensus in Go.

Work Experience
Software Engineering Intern (Summer 2023)
- Implemented backend APIs.
"""
    result = audit_section_flow(sample, is_early_career=True)
    assert result["flow_score"] >= 85
    assert result["benchmark_profile"] == "Early Career"
