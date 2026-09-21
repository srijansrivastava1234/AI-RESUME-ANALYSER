"""
Resume Page Budget & Spillover Hazard Analyzer
Evaluates token density, rendered line count estimations, and multi-page budget constraints.
Detects awkward trailing spillover hazards (e.g., 1.10 pages) that leave recruiters with
nearly-blank trailing pages in PDF previewers.
"""

import math
from typing import Dict, Any, List

# Standard typesetting constraints (Single column 10-11pt font with standard margins)
WORDS_PER_PAGE_OPTIMAL_MIN = 380
WORDS_PER_PAGE_OPTIMAL_MAX = 650
ESTIMATED_LINES_PER_PAGE = 50


def estimate_page_metrics(text: str) -> Dict[str, Any]:
    """
    Computes word counts, raw lines, non-empty content lines, and fractional page length.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    words = [w for w in text.split() if w.strip()]
    total_words = len(words)
    total_content_lines = len(lines)
    
    # Estimate rendered physical lines including wrapped lines (avg 12 words / line)
    wrapped_lines = sum(max(1, math.ceil(len(line.split()) / 12)) for line in lines)
    
    # Estimate fractional page count
    fractional_pages = round(max(0.1, wrapped_lines / ESTIMATED_LINES_PER_PAGE), 2)
    
    return {
        "total_words": total_words,
        "total_content_lines": total_content_lines,
        "estimated_rendered_lines": wrapped_lines,
        "fractional_pages": fractional_pages
    }


def audit_page_budget(text: str, target_pages: int = 1) -> Dict[str, Any]:
    """
    Audits page budget adherence and flags dangerous trailing spillover.
    """
    metrics = estimate_page_metrics(text)
    fractional_pages = metrics["fractional_pages"]
    total_words = metrics["total_words"]
    
    warnings: List[str] = []
    recommendations: List[str] = []
    penalties = 0
    spillover_detected = False
    
    # Determine spillover condition (e.g. 1.05 - 1.25 or 2.05 - 2.25)
    page_remainder = fractional_pages - math.floor(fractional_pages)
    if (fractional_pages > 1.0 and page_remainder > 0.04 and page_remainder <= 0.28):
        spillover_detected = True
        warnings.append(
            f"Spillover Hazard Detected: Estimated {fractional_pages} pages. "
            f"Only a few lines will spill onto Page {math.ceil(fractional_pages)}, creating an unprofessional trailing orphan page."
        )
        penalties += 30
        recommendations.append(
            "Condense bullet points or trim 3-6 lines of text to fit cleanly on the preceding page."
        )

    # Validate against target page budget
    if target_pages == 1:
        if fractional_pages > 1.35:
            warnings.append(f"Content significantly exceeds 1-page target ({fractional_pages} pages estimated).")
            penalties += 20
            recommendations.append("For candidates with <5 years experience, target a tight single-page format.")
        elif total_words < WORDS_PER_PAGE_OPTIMAL_MIN:
            warnings.append(f"Content density is sparse ({total_words} words). The page may appear half-empty.")
            penalties += 20
            recommendations.append("Elaborate on technical achievements using XYZ metrics to fill visual whitespace.")
    elif target_pages == 2:
        if fractional_pages < 1.4:
            recommendations.append("Content is too brief for a 2-page resume. Either condense to 1 page or expand project impact.")
            penalties += 10
        elif fractional_pages > 2.3:
            warnings.append(f"Resume length ({fractional_pages} pages) exceeds standard 2-page corporate ceiling.")
            penalties += 25

    budget_score = max(0, 100 - penalties)
    
    return {
        "budget_score": budget_score,
        "is_within_budget": budget_score >= 80 and not spillover_detected,
        "spillover_detected": spillover_detected,
        "metrics": metrics,
        "target_pages": target_pages,
        "warnings": warnings,
        "recommendations": recommendations
    }
