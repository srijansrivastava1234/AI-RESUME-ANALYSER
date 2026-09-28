"""
Unit tests for export_formatter module.
"""

import pytest
from app.export_formatter import (
    sanitize_text_for_export,
    format_ats_markdown,
    format_ats_plaintext,
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
