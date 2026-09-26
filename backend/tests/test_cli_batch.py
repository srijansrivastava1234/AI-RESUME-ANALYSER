import os
import json
import pytest
from app.cli import run_batch_cli_audit

def test_run_batch_cli_audit_empty_dir(tmp_path):
    empty_dir = tmp_path / "empty_resumes"
    empty_dir.mkdir()
    
    summary = run_batch_cli_audit(str(empty_dir), quiet=True)
    assert summary["total_files"] == 0
    assert summary["average_score"] == 0.0
    assert len(summary["results"]) == 0

def test_run_batch_cli_audit_invalid_dir():
    with pytest.raises(NotADirectoryError):
        run_batch_cli_audit("non_existent_folder_xyz_123", quiet=True)

def test_run_batch_cli_audit_multiple_resumes(tmp_path):
    res_dir = tmp_path / "resumes"
    res_dir.mkdir()

    resume1 = res_dir / "alex_mercer.txt"
    resume1.write_text(
        "Alexander Mercer\nSenior Cloud Architect\nSkills: Python, AWS, Docker, Kubernetes\n"
        "Experience:\n- Spearheaded migration to Kubernetes reducing latency by 45% ($200k savings).\n",
        encoding="utf-8"
    )

    resume2 = res_dir / "jane_doe.txt"
    resume2.write_text(
        "Jane Doe\nJunior Developer\nSkills: Python, HTML, CSS\n"
        "Experience:\n- Assisted in web development bug fixes.\n",
        encoding="utf-8"
    )

    summary_file = tmp_path / "summary.json"

    summary = run_batch_cli_audit(
        directory_path=str(res_dir),
        output_summary_path=str(summary_file),
        quiet=True
    )

    assert summary["total_files"] == 2
    assert summary["successful_evaluations"] == 2
    assert summary["average_score"] > 0
    assert len(summary["rankings"]) == 2
    # Ensure rankings are sorted descending by ATS score
    assert summary["rankings"][0]["ats_score"] >= summary["rankings"][1]["ats_score"]
    assert os.path.exists(str(summary_file))
