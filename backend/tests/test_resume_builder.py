"""
Test suite for Phase 5: Structured Resume Parsing, State Model, and Plain-Text Generator.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.resume_builder import (
    extract_contact_info,
    split_resume_into_sections,
    parse_experience_section,
    parse_education_section,
    parse_skills_section,
    parse_projects_section,
    parse_resume_to_structured_json,
    format_structured_resume_to_plain_text
)

SAMPLE_RESUME = """
ALEX MERCER
San Francisco, CA | alex.mercer@example.com | (555) 123-4567 | linkedin.com/in/alexmercer | github.com/alexmercer

PROFESSIONAL SUMMARY
Results-oriented Senior Full-Stack Engineer with 7+ years of experience scaling distributed cloud systems and AI pipelines.

WORK EXPERIENCE
Senior Software Engineer | Acme Corporation | 2021 - Present
• Architected high-throughput microservices in Go and Python reducing p99 latency by 42%.
• Led a squad of 6 engineers migrating legacy monolithic database to PostgreSQL with zero downtime.
• Integrated Redis caching layer saving $18,000 monthly cloud infrastructure cost.

Software Engineer | BetaTech Labs | 2018 - 2021
• Developed React and Node.js customer portal serving 250,000 daily active users.
• Built automated CI/CD pipeline using Docker and GitHub Actions cutting deploy cycle by 65%.

TECHNICAL SKILLS
Languages & Core: Python, Go, TypeScript, JavaScript, SQL
Tools & Technologies: Docker, Kubernetes, AWS, PostgreSQL, Redis, Git, CI/CD
Leadership & Practices: Agile, Scrum, Mentorship, System Architecture

EDUCATION
B.S. in Computer Science | University of California, Berkeley | 2018
GPA: 3.8 / 4.0

PROJECTS
CloudScale Monitoring | Go, Docker, Prometheus
• Built real-time container metrics ingestion engine processing 50k events/sec.

CERTIFICATIONS
• AWS Certified Solutions Architect - Professional
• Certified Kubernetes Administrator (CKA)
"""

client = TestClient(app)

def test_extract_contact_info():
    contact = extract_contact_info(SAMPLE_RESUME)
    assert "Alex Mercer" in contact["full_name"] or "ALEX MERCER" in contact["full_name"]
    assert contact["email"] == "alex.mercer@example.com"
    assert "555" in contact["phone"]
    assert "linkedin.com/in/alexmercer" in contact["linkedin"]
    assert "github.com/alexmercer" in contact["github"]
    assert "San Francisco" in contact["location"]

def test_split_resume_into_sections():
    sections = split_resume_into_sections(SAMPLE_RESUME)
    assert "summary" in sections
    assert "experience" in sections
    assert "skills" in sections
    assert "education" in sections
    assert "projects" in sections
    assert "certifications" in sections

def test_parse_experience_section():
    sections = split_resume_into_sections(SAMPLE_RESUME)
    exp = parse_experience_section(sections["experience"])
    assert len(exp) >= 2
    assert "Senior Software Engineer" in exp[0]["role"]
    assert "Acme" in exp[0]["company"]
    assert len(exp[0]["bullets"]) >= 2
    assert any("p99 latency" in b for b in exp[0]["bullets"])

def test_parse_skills_section():
    sections = split_resume_into_sections(SAMPLE_RESUME)
    skills = parse_skills_section(sections["skills"])
    assert "Python" in skills["technical"] or any("Python" in s for s in skills["technical"])
    assert len(skills["tools_frameworks"]) > 0 or len(skills["technical"]) > 0

def test_parse_education_section():
    sections = split_resume_into_sections(SAMPLE_RESUME)
    edu = parse_education_section(sections["education"])
    assert len(edu) >= 1
    assert "Berkeley" in edu[0]["institution"] or "Computer Science" in edu[0]["degree"]
    assert edu[0]["grad_year"] == "2018"

def test_parse_resume_to_structured_json():
    data = parse_resume_to_structured_json(SAMPLE_RESUME)
    assert "contact" in data
    assert "experience" in data
    assert "education" in data
    assert "skills" in data
    assert len(data["experience"]) >= 2
    assert len(data["education"]) >= 1

def test_format_structured_resume_to_plain_text():
    data = parse_resume_to_structured_json(SAMPLE_RESUME)
    plain = format_structured_resume_to_plain_text(data)
    assert "ALEX MERCER" in plain
    assert "WORK EXPERIENCE" in plain
    assert "TECHNICAL SKILLS" in plain
    assert "EDUCATION" in plain
    assert "•" in plain

def test_parse_empty_resume():
    data = parse_resume_to_structured_json("")
    assert data["contact"]["full_name"] == "Candidate Name"
    assert len(data["experience"]) == 0
    assert len(data["education"]) == 0

def test_api_parse_structured_endpoint():
    res = client.post("/api/resume/parse-structured", json={"resume_text": SAMPLE_RESUME})
    assert res.status_code == 200
    json_data = res.json()
    assert "structured_resume" in json_data
    assert json_data["structured_resume"]["contact"]["email"] == "alex.mercer@example.com"

def test_api_format_clean_txt_endpoint():
    parsed = parse_resume_to_structured_json(SAMPLE_RESUME)
    res = client.post("/api/resume/format-clean-txt", json={"structured_resume": parsed})
    assert res.status_code == 200
    json_data = res.json()
    assert "plain_text" in json_data
    assert "ALEX MERCER" in json_data["plain_text"]
