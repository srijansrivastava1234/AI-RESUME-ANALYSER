import os
import pytest
from backend.app.cli import run_cli_audit

def test_cli_audit_with_simulation_and_security(tmp_path):
    resume_file = tmp_path / "sample_resume.txt"
    resume_file.write_text("""
    Jane Doe
    jane.doe@example.com | (555) 123-4567
    
    Work Experience
    Senior Software Engineer - CloudTech (2020 - 2026)
    • Architected distributed systems in Python and Go with AWS and PostgreSQL.
    • Improved latency by 35% across 10 microservices.
    
    Education
    Bachelor of Science in CS, Tech University (2016 - 2020)
    
    Skills
    Python, Go, AWS, Docker, Kubernetes, PostgreSQL, React
    """, encoding="utf-8")

    out_json = tmp_path / "report.json"
    badge_svg = tmp_path / "badge.svg"

    report = run_cli_audit(
        resume_path=str(resume_file),
        output_json_path=str(out_json),
        badge_svg_path=str(badge_svg),
        simulate=True,
        audit_security=True,
        quiet=True
    )

    assert report["ats_score"] > 0
    assert "ats_simulation" in report
    sim = report["ats_simulation"]
    assert "lever" in sim["engines"]
    assert "successfactors" in sim["engines"]
    assert "workday" in sim["engines"]
    assert "greenhouse" in sim["engines"]
    assert "taleo" in sim["engines"]
    assert "icims" in sim["engines"]
    assert sim["overall_cross_ats_score"] >= 70

    assert "adversarial_security" in report
    assert report["adversarial_security"]["is_adversarial"] is False

    assert os.path.exists(out_json)
    assert os.path.exists(badge_svg)
