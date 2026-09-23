"""
Test suite for Phase 7: Standalone CLI and Dynamic SVG Status Badge Generator.
"""

import os
import tempfile
import pytest
from app.cli import generate_svg_badge, run_cli_audit, parse_resume_file

SAMPLE_RESUME_TXT = """
ALEX MERCER
San Francisco, CA | alex.mercer@example.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced Senior Software Engineer with 7+ years building cloud services.

WORK EXPERIENCE
Senior Software Engineer | Acme Corp | 2021 - Present
• Architected high-throughput microservices in Go and Python reducing latency by 40%.
• Migrated database to PostgreSQL with zero downtime.

TECHNICAL SKILLS
Languages: Python, Go, TypeScript, SQL
Tools: Docker, Kubernetes, AWS, Git

EDUCATION
B.S. in Computer Science | UC Berkeley | 2018
"""

SAMPLE_JD_TXT = """
Job Title: Senior Software Engineer
Company: CloudScale Inc
Required: Python, Go, Docker, Kubernetes, AWS, PostgreSQL
"""

def test_generate_svg_badge_high_score():
    svg = generate_svg_badge(95)
    assert "<svg" in svg
    assert "95/100 • A+" in svg
    assert "#10b981" in svg

def test_generate_svg_badge_mid_score():
    svg = generate_svg_badge(65)
    assert "<svg" in svg
    assert "65/100 • C" in svg
    assert "#f59e0b" in svg

def test_generate_svg_badge_low_score():
    svg = generate_svg_badge(40)
    assert "<svg" in svg
    assert "40/100 • D" in svg
    assert "#ef4444" in svg

def test_parse_resume_file_txt():
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
        f.write(SAMPLE_RESUME_TXT)
        tmp_name = f.name

    try:
        extracted = parse_resume_file(tmp_name)
        assert "Alex Mercer" in extracted or "ALEX MERCER" in extracted
        assert "Acme Corp" in extracted
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

def test_run_cli_audit_with_outputs():
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as rf:
        rf.write(SAMPLE_RESUME_TXT)
        resume_tmp = rf.name

    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as jf:
        jf.write(SAMPLE_JD_TXT)
        jd_tmp = jf.name

    out_json = resume_tmp + ".json"
    out_svg = resume_tmp + ".svg"

    try:
        report = run_cli_audit(
            resume_path=resume_tmp,
            jd_path=jd_tmp,
            output_json_path=out_json,
            badge_svg_path=out_svg,
            quiet=True
        )

        assert "ats_score" in report
        assert report["ats_score"] > 0
        assert os.path.exists(out_json)
        assert os.path.exists(out_svg)

        with open(out_svg, "r", encoding="utf-8") as sf:
            svg_data = sf.read()
            assert "<svg" in svg_data
    finally:
        for p in [resume_tmp, jd_tmp, out_json, out_svg]:
            if os.path.exists(p):
                os.remove(p)
