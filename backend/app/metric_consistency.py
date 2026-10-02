"""Metric Verifiability & Baseline Denominator Calibrator.

Analyzes numerical claims, percentages, dollar values, and latency metrics across
resume bullets to evaluate quantitative credibility, detect unbounded/implausible
claims, and measure the baseline context attachment rate.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


# Regex patterns for various metric categories
PERCENTAGE_PATTERN = re.compile(
    r"(?P<val>[+-]?\d+(?:\.\d+)?)\s*%",
    re.IGNORECASE,
)
MULTIPLIER_PATTERN = re.compile(
    r"(?P<val>\d+(?:\.\d+)?)\s*(?:x|x-fold|fold)\b",
    re.IGNORECASE,
)
CURRENCY_PATTERN = re.compile(
    r"[\$\£\€\₹]\s*(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[kKmMbBtT]|thousand|million|billion)?\b",
    re.IGNORECASE,
)
LATENCY_THROUGHPUT_PATTERN = re.compile(
    r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>ms|milliseconds?|seconds?|qps|tps|req/sec|rps|reqs/sec|gbps|mbps)\b",
    re.IGNORECASE,
)
RAW_COUNT_PATTERN = re.compile(
    r"\b(?P<val>\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(?P<unit>[kKmMbB])?\s+(?P<noun>users|clients|customers|requests|queries|nodes|servers|engineers|microservices|pipelines|endpoints|pull requests|tickets|prs)\b",
    re.IGNORECASE,
)

# Patterns that indicate baseline / contextual denominator (e.g. "from X to Y", "down from", "compared to")
BASELINE_CONTEXT_PATTERN = re.compile(
    r"\b(?:from\s+[\$\£\€\₹]?\d+[\w%/\.]*\s+to\s+[\$\£\€\₹]?\d+[\w%/\.]*|down\s+from|up\s+from|reduced\s+from|compared\s+to|baseline\s+of|saving\s+[\$\£\€\₹]?\d+|previously\s+[\$\£\€\₹]?\d+|from\s+\d+ms\s+to\s+\d+ms)\b",
    re.IGNORECASE,
)

# Implausible / unbounded claim keywords
IMPLAUSIBLE_PATTERNS = [
    re.compile(r"\b(?:10000%|1000%|0\s+bugs|zero\s+downtime\s+for\s+\d+\s+years|100%\s+bug-free|100%\s+accurate|infinitely\s+scalable)\b", re.IGNORECASE),
]


def audit_metric_verifiability(text: str) -> Dict[str, Any]:
    """Audits the resume text for quantitative metric credibility and baseline denominator attachment.

    Args:
        text: Raw resume plain text.

    Returns:
        Dict containing:
            - verifiability_score: float (0.0 to 100.0)
            - total_metrics_found: int
            - baseline_attached_count: int
            - baseline_attachment_rate: float (0.0 to 1.0)
            - metric_breakdown: Dict of categorized counts
            - implausible_claims: List[str]
            - bullet_evaluations: List[Dict] with per-bullet findings
            - recommendations: List[str]
    """
    if not text or not text.strip():
        return {
            "verifiability_score": 0.0,
            "total_metrics_found": 0,
            "baseline_attached_count": 0,
            "baseline_attachment_rate": 0.0,
            "metric_breakdown": {
                "percentages": 0,
                "multipliers": 0,
                "currency": 0,
                "latency_throughput": 0,
                "raw_counts": 0,
            },
            "implausible_claims": [],
            "bullet_evaluations": [],
            "recommendations": ["No text provided for metric quantification auditing."],
        }

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    total_percentages = 0
    total_multipliers = 0
    total_currency = 0
    total_latency_throughput = 0
    total_raw_counts = 0
    
    baseline_attached_count = 0
    total_metrics_count = 0
    implausible_claims: List[str] = []
    bullet_evaluations: List[Dict[str, Any]] = []

    for line in lines:
        # Check if line looks like an experience bullet or metric-bearing claim
        p_matches = list(PERCENTAGE_PATTERN.finditer(line))
        m_matches = list(MULTIPLIER_PATTERN.finditer(line))
        c_matches = list(CURRENCY_PATTERN.finditer(line))
        lt_matches = list(LATENCY_THROUGHPUT_PATTERN.finditer(line))
        rc_matches = list(RAW_COUNT_PATTERN.finditer(line))

        line_metric_count = len(p_matches) + len(m_matches) + len(c_matches) + len(lt_matches) + len(rc_matches)
        if line_metric_count == 0:
            continue

        total_percentages += len(p_matches)
        total_multipliers += len(m_matches)
        total_currency += len(c_matches)
        total_latency_throughput += len(lt_matches)
        total_raw_counts += len(rc_matches)
        total_metrics_count += line_metric_count

        has_baseline = bool(BASELINE_CONTEXT_PATTERN.search(line))
        if has_baseline:
            baseline_attached_count += 1

        # Check for implausible claims
        for imp_pat in IMPLAUSIBLE_PATTERNS:
            match = imp_pat.search(line)
            if match:
                implausible_claims.append(f"Suspiciously absolute claim: '{match.group(0)}' in: {line[:80]}...")

        bullet_evaluations.append({
            "bullet": line if len(line) <= 120 else line[:117] + "...",
            "metrics_count": line_metric_count,
            "has_baseline_denominator": has_baseline,
            "detected_figures": [m.group(0) for m in (p_matches + m_matches + c_matches + lt_matches + rc_matches)],
        })

    # Calculate baseline attachment rate
    attachment_rate = (
        round(baseline_attached_count / len(bullet_evaluations), 2)
        if bullet_evaluations
        else 0.0
    )

    # Compute Verifiability Score (0-100)
    # Base: metrics volume (up to 40 pts), baseline attachment (up to 40 pts), diversity of units (up to 20 pts)
    volume_score = min(40.0, total_metrics_count * 5.0)
    baseline_score = attachment_rate * 40.0
    
    unique_categories = sum(
        1 for cnt in [
            total_percentages,
            total_multipliers,
            total_currency,
            total_latency_throughput,
            total_raw_counts,
        ]
        if cnt > 0
    )
    diversity_score = min(20.0, unique_categories * 5.0)

    raw_score = volume_score + baseline_score + diversity_score
    
    # Penalize for implausible claims
    penalty = min(30.0, len(implausible_claims) * 15.0)
    verifiability_score = max(0.0, min(100.0, round(raw_score - penalty, 1)))

    # Generate actionable recommendations
    recommendations: List[str] = []
    if total_metrics_count < 4:
        recommendations.append(
            "Low quantification density: Add at least 4-6 verifiable numerical results across key career accomplishments."
        )
    if attachment_rate < 0.35 and total_metrics_count > 0:
        recommendations.append(
            "Missing baseline denominators: Ground percentage improvements with explicit 'from X to Y' comparisons (e.g. 'Reduced p99 latency by 35% from 180ms to 117ms')."
        )
    if implausible_claims:
        recommendations.append(
            "Mitigate absolute claims: Replace sweeping absolutes (e.g. '0 bugs', '100% bug-free') with audit-defensible engineering metrics."
        )
    if total_currency == 0 and total_metrics_count >= 5:
        recommendations.append(
            "Add financial/budget context: Mention cost savings, cloud expenditure reductions, or revenue enablement if applicable."
        )
    if not recommendations:
        recommendations.append(
            "Excellent metric verifiability and contextual grounding across achievements."
        )

    return {
        "verifiability_score": verifiability_score,
        "total_metrics_found": total_metrics_count,
        "baseline_attached_count": baseline_attached_count,
        "baseline_attachment_rate": attachment_rate,
        "metric_breakdown": {
            "percentages": total_percentages,
            "multipliers": total_multipliers,
            "currency": total_currency,
            "latency_throughput": total_latency_throughput,
            "raw_counts": total_raw_counts,
        },
        "implausible_claims": implausible_claims,
        "bullet_evaluations": bullet_evaluations,
        "recommendations": recommendations,
    }
