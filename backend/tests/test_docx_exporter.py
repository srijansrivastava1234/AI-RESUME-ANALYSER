"""
Unit tests for DOCX resume generator.
"""

import docx
from app.docx_exporter import build_ats_docx_resume

SAMPLE_SCHEMA_DATA = {
    "contact": {
        "name": "David Miller",
        "email": "david.miller@example.com",
        "phone": "415-555-0182",
        "location": "San Francisco, CA"
    },
    "summary": "Accomplished Cloud Infrastructure Engineer with 6+ years experience.",
    "experience": [
        {
            "role": "Staff SRE",
            "company": "Apex Cloud",
            "dates": "2021 - Present",
            "bullets": [
                "Architected Kubernetes multi-region failover cluster reducing downtime to 0.001%.",
                "Automated Terraform infrastructure cutting provisioning time by 70%."
            ]
        }
    ],
    "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "Python", "Go"],
    "education": [
        {
            "degree": "B.S. in Software Engineering",
            "institution": "San Jose State University",
            "year": "2018"
        }
    ]
}

def test_build_ats_docx_resume():
    stream = build_ats_docx_resume(SAMPLE_SCHEMA_DATA)
    assert stream is not None
    assert stream.getvalue() != b""
    
    # Verify resulting document structure
    doc = docx.Document(stream)
    text_content = "\n".join([p.text for p in doc.paragraphs])
    
    assert "David Miller" in text_content
    assert "david.miller@example.com" in text_content
    assert "PROFESSIONAL SUMMARY" in text_content
    assert "WORK EXPERIENCE" in text_content
    assert "Staff SRE" in text_content
    assert "Apex Cloud" in text_content
    assert "TECHNICAL SKILLS" in text_content
    assert "Kubernetes" in text_content
    assert "EDUCATION" in text_content
