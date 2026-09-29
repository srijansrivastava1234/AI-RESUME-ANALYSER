"""
Unit tests for resume revision diff engine.
"""

from app.revision_diff import compute_resume_diff

def test_compute_resume_diff_positive():
    base = {
        "ats_score": 65,
        "keywords": {"found": ["Python", "SQL"], "missing": ["Docker", "Kubernetes", "AWS"]},
        "metrics": [{"name": "Hard Skills", "score": 60}],
        "improvements": ["Add Docker", "Add Kubernetes", "Add AWS"]
    }
    rev = {
        "ats_score": 85,
        "keywords": {"found": ["Python", "SQL", "Docker", "AWS"], "missing": ["Kubernetes"]},
        "metrics": [{"name": "Hard Skills", "score": 85}],
        "improvements": ["Add Kubernetes"]
    }
    
    diff = compute_resume_diff(base, rev)
    assert diff["score_delta"] == 20
    assert diff["verdict"] == "Significant Optimization"
    assert "Docker" in diff["resolved_keyword_gaps"]
    assert "AWS" in diff["resolved_keyword_gaps"]
    assert "Docker" in diff["newly_added_keywords"]
    assert diff["metric_deltas"][0]["delta"] == 25
    assert diff["metric_deltas"][0]["status"] == "improved"

def test_compute_resume_diff_regression():
    base = {
        "ats_score": 80,
        "keywords": {"found": ["Python", "AWS"], "missing": []},
        "metrics": [{"name": "Keywords", "score": 80}],
        "improvements": []
    }
    rev = {
        "ats_score": 70,
        "keywords": {"found": ["Python"], "missing": ["AWS"]},
        "metrics": [{"name": "Keywords", "score": 70}],
        "improvements": ["Add AWS"]
    }
    
    diff = compute_resume_diff(base, rev)
    assert diff["score_delta"] == -10
    assert diff["verdict"] == "Score Regression Detected"
    assert "AWS" in diff["new_keyword_gaps"]
