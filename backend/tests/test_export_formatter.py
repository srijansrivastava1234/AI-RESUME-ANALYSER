"""
Unit tests for export_formatter module.
"""

import pytest
from app.export_formatter import (
    sanitize_text_for_export,
    format_ats_markdown,
    format_ats_plaintext,
    format_ats_jsonld,
    TYPOGRAPHIC_REPLACEMENTS
)


def test_sanitize_text_for_export():
    sample = "He said \u201cHello\u201d \u2014 here\u2019s a bullet \u2022 item with a ligature \ufb01le."
    clean = sanitize_text_for_export(sample)
    assert '"Hello"' in clean
    assert " - " in clean
    assert "here's" in clean
    assert "*" in clean
    assert "file" in clean


def test_format_ats_markdown_empty():
    assert format_ats_markdown({}) == ""


def test_format_ats_markdown_structured():
    data = {
        "name": "Jane Developer",
        "title": "Senior Cloud Engineer",
        "email": "jane@example.com",
        "phone": "(555) 123-4567",
        "location": "New York, NY",
        "summary": "Experienced engineer with 7+ years in distributed systems.",
        "skills": {
            "Languages": ["Python", "Go", "TypeScript"],
            "Cloud": ["AWS", "Kubernetes", "Terraform"]
        },
        "experience": [
            {
                "role": "Staff Engineer",
                "company": "Tech Corp",
                "dates": "2021 - Present",
                "location": "Remote",
                "bullets": [
                    "Architected high-throughput microservices handling 250k RPS.",
                    "Reduced AWS infrastructure costs by 40% using spot instances."
                ]
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "MIT",
                "year": 2018
            }
        ]
    }

    md = format_ats_markdown(data)
    assert "# Jane Developer" in md
    assert "**Senior Cloud Engineer**" in md
    assert "jane@example.com | (555) 123-4567 | New York, NY" in md
    assert "## Professional Summary" in md
    assert "## Technical Skills" in md
    assert "- **Languages:** Python, Go, TypeScript" in md
    assert "### Staff Engineer | Tech Corp | 2021 - Present (Remote)" in md
    assert "- Architected high-throughput microservices handling 250k RPS." in md
    assert "## Education" in md
    assert "- **B.S. in Computer Science**, MIT (2018)" in md


def test_format_ats_plaintext():
    data = {
        "name": "John Doe",
        "title": "Software Engineer",
        "summary": "Full-stack developer building robust APIs.",
        "skills": ["Python", "FastAPI", "Docker"]
    }
    plain = format_ats_plaintext(data)
    assert "John Doe" in plain
    assert "Software Engineer" in plain
    assert "Technical Skills" in plain
    assert "Python, FastAPI, Docker" in plain
    assert "#" not in plain


def test_export_json_resume_schema():
    from app.schema_exporter import export_json_resume_schema
    data = {
        "contact": {
            "name": "Jane Developer",
            "title": "Senior Cloud Engineer",
            "email": "jane@example.com",
            "phone": "555-123-4567",
            "linkedin": "https://linkedin.com/in/janedev",
            "github": "https://github.com/janedev",
            "city": "Seattle",
            "region": "WA",
            "country": "US"
        },
        "summary": "Cloud Architect with deep AWS expertise.",
        "work_experience": [
            {
                "company": "CloudTech",
                "position": "Principal Architect",
                "start_date": "2020-01",
                "end_date": "Present",
                "bullets": ["Designed multi-region serverless infrastructure."]
            }
        ],
        "education": [
            {
                "institution": "University of Washington",
                "degree": "Computer Science",
                "study_type": "B.S.",
                "start_date": "2014",
                "end_date": "2018"
            }
        ],
        "skills": [
            {"category": "Cloud", "skills": ["AWS", "Kubernetes", "Terraform"]}
        ]
    }

    schema = export_json_resume_schema(data)
    assert schema["$schema"] == "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"
    assert schema["basics"]["name"] == "Jane Developer"
    assert schema["basics"]["email"] == "jane@example.com"
    assert len(schema["basics"]["profiles"]) == 2
    assert schema["work"][0]["name"] == "CloudTech"
    assert schema["education"][0]["institution"] == "University of Washington"
    assert schema["skills"][0]["name"] == "Cloud"


def test_sanitize_extended_typography():
    sample = "FastAPI\u2122 & Python\u00ae \u2014 \u201010% latency\u2026 \u00a92026 1\u20442 ratio"
    clean = sanitize_text_for_export(sample)
    assert "(tm)" in clean
    assert "(r)" in clean
    assert " - " in clean
    assert "-10%" in clean
    assert "..." in clean
    assert "(c)2026" in clean
    assert "1/2" in clean


def test_format_ats_jsonld_empty():
    assert format_ats_jsonld({}) == {}


def test_format_ats_jsonld_structured():
    data = {
        "name": "Jane Developer",
        "title": "Principal Architect",
        "email": "jane@example.com",
        "phone": "+1-555-0199",
        "location": "San Francisco, CA",
        "linkedin": "https://linkedin.com/in/janedev",
        "github": "https://github.com/janedev",
        "summary": "Specialist in large-scale event-driven cloud systems.",
        "skills": {
            "Languages": ["Python", "Rust"],
            "Databases": ["PostgreSQL"]
        },
        "experience": [
            {
                "role": "Staff Engineer",
                "company": "ScaleCorp",
                "dates": "2022 - Present",
                "bullets": ["Led migration to distributed Kafka pipelines."]
            }
        ],
        "education": [
            {
                "degree": "M.S. Software Engineering",
                "institution": "Stanford University",
                "year": 2020
            }
        ]
    }

    schema = format_ats_jsonld(data)
    assert schema["@context"] == "https://schema.org"
    assert schema["@type"] == "Person"
    assert schema["name"] == "Jane Developer"
    assert schema["jobTitle"] == "Principal Architect"
    assert schema["email"] == "jane@example.com"
    assert schema["telephone"] == "+1-555-0199"
    assert schema["address"]["addressLocality"] == "San Francisco, CA"
    assert "https://linkedin.com/in/janedev" in schema["sameAs"]
    assert "https://github.com/janedev" in schema["sameAs"]
    assert "Python" in schema["knowsAbout"]
    assert "Rust" in schema["knowsAbout"]
    assert schema["hasOccupation"][0]["roleName"] == "Staff Engineer"
    assert schema["hasOccupation"][0]["name"] == "ScaleCorp"
    assert schema["hasCredential"][0]["credentialCategory"] == "M.S. Software Engineering"
    assert schema["hasCredential"][0]["recognizedBy"]["name"] == "Stanford University"
    assert schema["hasCredential"][0]["validIn"] == "2020"
