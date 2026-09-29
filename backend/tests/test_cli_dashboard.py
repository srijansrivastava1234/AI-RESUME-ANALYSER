"""
Test suite for Interactive Rich CLI Dashboard & Visual Formatting Utilities.
"""

import os
import io
import sys
import tempfile
import pytest
from app.cli import (
    get_grade_info,
    render_progress_bar,
    generate_svg_badge,
    print_single_resume_dashboard,
    print_batch_dashboard,
    run_cli_audit,
    run_batch_cli_audit,
    Colors,
    colorize,
)

SAMPLE_RESUME = """
SARAH CONNOR
Austin, TX | sarah.connor@example.com | 512-555-0199
Senior DevOps & Cloud Infrastructure Engineer

EXPERIENCE
Lead DevOps Engineer | Cyberdyne Systems | 2021 - Present
- Architected zero-trust Kubernetes clusters across 3 AWS regions reducing MTTR by 60%.
- Automated CI/CD deployment pipelines with GitHub Actions cutting release cycle time by 45%.
- Implemented Prometheus and Grafana monitoring stack achieving 99.99% system availability.

TECHNICAL SKILLS
Cloud & DevOps: AWS, Kubernetes, Docker, Terraform, CI/CD, Helm, Linux
Languages: Python, Go, Bash, YAML

EDUCATION
B.S. in Computer Engineering | UT Austin | 2019
"""

SAMPLE_JD = """
Job Title: Senior Cloud & DevOps Engineer
Required Skills: AWS, Kubernetes, Docker, Terraform, CI/CD, Python, Linux
"""

def test_get_grade_info_all_tiers():
    assert get_grade_info(95)["grade"] == "A+"
    assert get_grade_info(85)["grade"] == "A"
    assert get_grade_info(75)["grade"] == "B"
    assert get_grade_info(65)["grade"] == "C"
    assert get_grade_info(40)["grade"] == "D"

def test_render_progress_bar():
    bar_high = render_progress_bar(90, width=20)
    assert len(bar_high) > 0
    bar_low = render_progress_bar(20, width=20)
    assert len(bar_low) > 0

def test_colorize_utility():
    colored = colorize("Test", Colors.GREEN)
    assert "Test" in colored

def test_print_single_resume_dashboard_stdout():
    report_data = {
        "ats_score": 88,
        "metrics": [
            {"name": "Hard Skills & Keywords", "score": 90, "feedback": "Excellent keyword coverage"},
            {"name": "Action Verbs & Impact", "score": 85, "feedback": "Strong quantified bullet points"},
        ],
        "key_strengths": ["Strong cloud orchestration experience", "Quantified business metrics"],
        "keywords": {"missing": ["Terraform", "Prometheus"]},
        "improvements": ["Elaborate on Helm and Kubernetes networking configuration"]
    }
    
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        print_single_resume_dashboard("sarah_connor_resume.pdf", report_data, jd_path="devops_jd.txt")
    finally:
        sys.stdout = old_stdout
        
    out = captured.getvalue()
    assert "AI RESUME ANALYSER" in out
    assert "Overall ATS Score" in out
    assert "88" in out
    assert "CORE AUDIT METRICS" in out

def test_print_batch_dashboard_stdout():
    batch_data = {
        "total_files": 2,
        "average_score": 82.5,
        "highest_score": 90,
        "lowest_score": 75,
        "rankings": [
            {"filename": "candidate_1.pdf", "ats_score": 90, "status": "success"},
            {"filename": "candidate_2.pdf", "ats_score": 75, "status": "success"},
        ]
    }
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        print_batch_dashboard(batch_data)
    finally:
        sys.stdout = old_stdout
        
    out = captured.getvalue()
    assert "BATCH RESUME LEADERBOARD" in out
    assert "candidate_1.pdf" in out
    assert "candidate_2.pdf" in out
    assert "90" in out

def test_cli_end_to_end_evaluation(tmp_path):
    resume_file = tmp_path / "sarah.txt"
    jd_file = tmp_path / "job.txt"
    out_json = tmp_path / "audit.json"
    out_badge = tmp_path / "badge.svg"
    
    resume_file.write_text(SAMPLE_RESUME, encoding="utf-8")
    jd_file.write_text(SAMPLE_JD, encoding="utf-8")
    
    report = run_cli_audit(
        resume_path=str(resume_file),
        jd_path=str(jd_file),
        output_json_path=str(out_json),
        badge_svg_path=str(out_badge),
        quiet=False
    )
    
    assert report["ats_score"] > 0
    assert os.path.exists(str(out_json))
    assert os.path.exists(str(out_badge))
