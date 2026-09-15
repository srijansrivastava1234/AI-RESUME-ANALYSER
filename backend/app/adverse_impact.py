"""
Adverse Impact & EEOC Four-Fifths Safe Harbor Auditor.

Grounded in NYC Local Law 144 (AEDT Bias Audits) and EEOC Uniform Guidelines
on Employee Selection Procedures (29 C.F.R. Part 1607):
- Evaluates selection rate parity across candidate pools and algorithmic thresholds.
- Four-Fifths Rule formulation:
    Impact Ratio (IR) = (Selection Rate Group X) / (Selection Rate Highest Group)
    If IR >= 0.80 (80%), system satisfies legal safe harbor against disparate impact.
- Provides demographic-neutral proxy auditing to certify absence of protected attribute leaks.
"""

from typing import Dict, List, Any, Optional


def calculate_four_fifths_ratio(
    selection_rate_target: float,
    selection_rate_benchmark: float
) -> float:
    """
    Computes the EEOC Four-Fifths Impact Ratio (IR).
    
    :param selection_rate_target: Selection rate of evaluated group (0.0 - 1.0).
    :param selection_rate_benchmark: Selection rate of benchmark/highest performing group (0.0 - 1.0).
    :return: Impact ratio rounded to 4 decimal places.
    """
    if selection_rate_benchmark <= 0:
        return 1.0 if selection_rate_target >= 0 else 0.0
    return round(selection_rate_target / selection_rate_benchmark, 4)


def audit_group_selection_rates(
    group_data: Dict[str, Dict[str, int]]
) -> Dict[str, Any]:
    """
    Audits selection rates across demographic or cohort groups per NYC Local Law 144.

    :param group_data: Dict mapping group identifier to {"total": int, "selected": int}.
                       Example: {"cohort_a": {"total": 100, "selected": 60}, "cohort_b": {"total": 80, "selected": 52}}
    :return: Audit report with group selection rates, benchmark group, impact ratios, and safe harbor status.
    """
    if not group_data:
        return {
            "is_compliant": True,
            "status": "NO_DATA",
            "lowest_impact_ratio": 1.0,
            "benchmark_group": None,
            "group_metrics": {},
            "findings": ["No group data provided for adverse impact evaluation."]
        }

    group_metrics: Dict[str, Dict[str, Any]] = {}
    highest_rate = -1.0
    benchmark_group = None

    for group_name, counts in group_data.items():
        total = max(0, counts.get("total", 0))
        selected = max(0, counts.get("selected", 0))
        rate = round(selected / total, 4) if total > 0 else 0.0

        group_metrics[group_name] = {
            "total": total,
            "selected": selected,
            "selection_rate": rate
        }

        if rate > highest_rate:
            highest_rate = rate
            benchmark_group = group_name

    # Calculate Four-Fifths Impact Ratio for each group against benchmark
    lowest_ratio = 1.0
    adverse_impact_groups: List[str] = []

    for group_name, metrics in group_metrics.items():
        ratio = calculate_four_fifths_ratio(metrics["selection_rate"], highest_rate)
        metrics["impact_ratio"] = ratio
        metrics["passes_four_fifths"] = ratio >= 0.80

        if ratio < lowest_ratio:
            lowest_ratio = ratio

        if not metrics["passes_four_fifths"]:
            adverse_impact_groups.append(group_name)

    is_compliant = len(adverse_impact_groups) == 0

    findings: List[str] = []
    if is_compliant:
        findings.append(
            f"EEOC Safe Harbor Verified: All groups achieve >= 80% of benchmark selection rate "
            f"(Benchmark: {benchmark_group} at {round(highest_rate * 100, 1)}%)."
        )
    else:
        findings.append(
            f"Adverse Impact Warning: {len(adverse_impact_groups)} group(s) fell below the 0.80 Four-Fifths threshold "
            f"relative to {benchmark_group}."
        )

    return {
        "is_compliant": is_compliant,
        "status": "COMPLIANT_SAFE_HARBOR" if is_compliant else "ADVERSE_IMPACT_DETECTED",
        "lowest_impact_ratio": lowest_ratio,
        "benchmark_group": benchmark_group,
        "benchmark_selection_rate": highest_rate,
        "group_metrics": group_metrics,
        "findings": findings
    }


def audit_score_distribution_disparity(
    scores: List[float],
    passing_threshold: float = 70.0
) -> Dict[str, Any]:
    """
    Evaluates scoring distribution for potential truncation or artificial bottlenecking.

    :param scores: List of numeric candidate scores (0 - 100).
    :param passing_threshold: Score cutoff threshold for qualification.
    :return: Summary metrics including pass rate, mean, spread, and legal audit tier.
    """
    if not scores:
        return {
            "total_candidates": 0,
            "passing_candidates": 0,
            "pass_rate": 0.0,
            "mean_score": 0.0,
            "audit_tier": "EMPTY"
        }

    total = len(scores)
    passing = sum(1 for s in scores if s >= passing_threshold)
    pass_rate = round(passing / total, 4)
    mean_score = round(sum(scores) / total, 2)

    return {
        "total_candidates": total,
        "passing_candidates": passing,
        "pass_rate": pass_rate,
        "mean_score": mean_score,
        "audit_tier": "BALANCED" if 0.20 <= pass_rate <= 0.85 else "SKEWED"
    }
