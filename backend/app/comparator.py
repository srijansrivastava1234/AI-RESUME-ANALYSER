"""
Multi-resume comparison engine for batch-ranking resumes against a single
job description. Enables side-by-side ATS score comparison to identify
the strongest resume version.
"""

import logging
from typing import Optional
from app.analyzer import analyze_resume

logger = logging.getLogger("ResumeComparator")


def compare_resumes(
    resume_texts: list[dict],
    job_description: Optional[str] = None
) -> dict:
    """
    Analyzes multiple resumes against a single job description and
    returns a ranked comparison report.

    :param resume_texts: List of dicts with 'filename' and 'text' keys
    :param job_description: Optional target job description for scoring
    :return: Comparison report with ranked results and summary
    """
    if not resume_texts or len(resume_texts) < 2:
        raise ValueError("At least 2 resumes are required for comparison.")

    if len(resume_texts) > 5:
        raise ValueError("Maximum 5 resumes can be compared at once.")

    results = []

    for idx, resume_entry in enumerate(resume_texts):
        filename = resume_entry.get("filename", f"resume_{idx + 1}")
        text = resume_entry.get("text", "")

        if not text.strip():
            logger.warning(f"Skipping empty resume: {filename}")
            continue

        logger.info(f"Analyzing resume {idx + 1}/{len(resume_texts)}: {filename}")
        report = analyze_resume(text, job_description)

        results.append({
            "rank": 0,  # Will be set after sorting
            "filename": filename,
            "ats_score": report.get("ats_score", 0),
            "job_compatibility_score": (
                report.get("job_compatibility", {}).get("score")
                if report.get("job_compatibility")
                else None
            ),
            "detected_keywords_count": len(
                report.get("keywords", {}).get("detected", [])
            ),
            "missing_keywords_count": len(
                report.get("keywords", {}).get("missing", [])
            ),
            "key_strengths": report.get("key_strengths", []),
            "report": report,
        })

    # Sort by ATS score descending
    results.sort(key=lambda x: x["ats_score"], reverse=True)

    # Assign ranks
    for i, result in enumerate(results):
        result["rank"] = i + 1

    # Generate comparison summary
    if len(results) >= 2:
        best = results[0]
        runner_up = results[1]
        score_gap = best["ats_score"] - runner_up["ats_score"]
        summary = (
            f"'{best['filename']}' ranks #1 with an ATS score of "
            f"{best['ats_score']}/100, leading by {score_gap} points over "
            f"'{runner_up['filename']}' ({runner_up['ats_score']}/100)."
        )
    else:
        summary = "Insufficient resumes for comparison ranking."

    return {
        "total_compared": len(results),
        "summary": summary,
        "rankings": results,
    }
