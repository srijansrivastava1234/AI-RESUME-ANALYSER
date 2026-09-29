"""
Module: revision_diff.py
Purpose: Compares two resume versions (v1 Baseline vs v2 Revision) to compute
net ATS score delta, resolved keyword gaps, regressions, and bullet improvements.
"""

from typing import Dict, Any, List


def compute_resume_diff(
    baseline_report: Dict[str, Any],
    revised_report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes a structured diff and delta analysis between two resume audit reports.
    """
    base_score = int(baseline_report.get("ats_score", 0))
    rev_score = int(revised_report.get("ats_score", 0))
    score_delta = rev_score - base_score

    # Keyword diffing
    base_kws = set(baseline_report.get("keywords", {}).get("found", []))
    rev_kws = set(revised_report.get("keywords", {}).get("found", []))
    base_missing = set(baseline_report.get("keywords", {}).get("missing", []))
    rev_missing = set(revised_report.get("keywords", {}).get("missing", []))

    newly_added_kws = sorted(list(rev_kws - base_kws))
    resolved_gaps = sorted(list(base_missing - rev_missing))
    new_unresolved_gaps = sorted(list(rev_missing - base_missing))

    # Metric comparison
    base_metrics = {m.get("name", ""): m.get("score", 0) for m in baseline_report.get("metrics", [])}
    rev_metrics = {m.get("name", ""): m.get("score", 0) for m in revised_report.get("metrics", [])}
    
    metric_deltas = []
    all_metric_names = sorted(list(set(base_metrics.keys()) | set(rev_metrics.keys())))
    for name in all_metric_names:
        b_val = base_metrics.get(name, 0)
        r_val = rev_metrics.get(name, 0)
        metric_deltas.append({
            "name": name,
            "baseline_score": b_val,
            "revised_score": r_val,
            "delta": r_val - b_val,
            "status": "improved" if r_val > b_val else ("regressed" if r_val < b_val else "unchanged")
        })

    # Summary assessment
    if score_delta >= 15:
        verdict = "Significant Optimization"
    elif score_delta > 0:
        verdict = "Moderate Improvement"
    elif score_delta == 0:
        verdict = "Neutral (No Net Score Change)"
    else:
        verdict = "Score Regression Detected"

    return {
        "baseline_score": base_score,
        "revised_score": rev_score,
        "score_delta": score_delta,
        "verdict": verdict,
        "newly_added_keywords": newly_added_kws,
        "resolved_keyword_gaps": resolved_gaps,
        "new_keyword_gaps": new_unresolved_gaps,
        "metric_deltas": metric_deltas,
        "improvements_count_delta": len(revised_report.get("improvements", [])) - len(baseline_report.get("improvements", []))
    }
