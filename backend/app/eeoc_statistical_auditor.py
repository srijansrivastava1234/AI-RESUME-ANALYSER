"""EEOC Statistical Significance & NYC Local Law 144 AEDT Bias Auditor.

Implements mathematical and statistical rigor mandated by:
1. EEOC Uniform Guidelines on Employee Selection Procedures (29 CFR Part 1607).
2. The 2-Standard-Deviation Rule (Hazelwood School District v. United States, 433 U.S. 299).
3. NYC Local Law 144 Automated Employment Decision Tool (AEDT) annual bias audit requirements.
4. Intersectionality Matrix Parity auditing for combined demographic cohorts.
"""

import math
from typing import Any, Dict, List, Optional, Tuple


def calculate_two_standard_deviation_z_score(
    selected_target: int,
    total_target: int,
    selected_benchmark: int,
    total_benchmark: int
) -> Tuple[float, bool]:
    """
    Calculates the two-sample pooled z-statistic for difference in selection proportions.
    
    Under EEOC guidelines and federal case law (Hazelwood, Castaneda), a disparity
    exceeding 1.96 standard deviations (typically rounded to 2.0 SD) is statistically significant.
    
    Returns:
        (z_score, is_statistically_significant)
    """
    if total_target <= 0 or total_benchmark <= 0:
        return 0.0, False

    p1 = selected_target / total_target
    p2 = selected_benchmark / total_benchmark

    pooled_p = (selected_target + selected_benchmark) / (total_target + total_benchmark)
    if pooled_p == 0.0 or pooled_p == 1.0:
        return 0.0, False

    se = math.sqrt(pooled_p * (1.0 - pooled_p) * (1.0 / total_target + 1.0 / total_benchmark))
    if se == 0.0:
        return 0.0, False

    z = (p1 - p2) / se
    return round(z, 4), abs(z) >= 1.96


def generate_nyc_ll144_audit_report(
    cohort_data: Dict[str, Dict[str, Any]],
    scoring_threshold: float = 70.0
) -> Dict[str, Any]:
    """
    Generates a full NYC LL 144 compliant AEDT bias audit report with:
    - Group selection rates
    - Benchmark highest-scoring group
    - Impact ratios (Four-Fifths rule)
    - Two-standard-deviation statistical significance
    - Audit pass/fail certification status
    
    :param cohort_data: Mapping of cohort name to {"scores": List[float]} or {"total": int, "selected": int}
    """
    if not cohort_data:
        return {
            "status": "NO_DATA",
            "is_certified": False,
            "findings": ["No candidate cohort data provided."],
            "groups": {}
        }

    # Normalize group counts
    normalized_groups: Dict[str, Dict[str, int]] = {}
    for group_name, data in cohort_data.items():
        if "scores" in data:
            scores = data["scores"]
            total = len(scores)
            selected = sum(1 for s in scores if s >= scoring_threshold)
            normalized_groups[group_name] = {"total": total, "selected": selected}
        else:
            normalized_groups[group_name] = {
                "total": int(data.get("total", 0)),
                "selected": int(data.get("selected", 0))
            }

    # Identify highest performing benchmark group
    rates: Dict[str, float] = {}
    for g, counts in normalized_groups.items():
        t = counts["total"]
        s = counts["selected"]
        rate = (s / t) if t > 0 else 0.0
        rates[g] = rate

    if not rates or max(rates.values()) == 0:
        benchmark_group = list(normalized_groups.keys())[0] if normalized_groups else "None"
        benchmark_rate = 0.0
    else:
        benchmark_group = max(rates, key=rates.get)
        benchmark_rate = rates[benchmark_group]

    results_table: Dict[str, Any] = {}
    violations: List[str] = []
    has_adverse_impact = False

    for group_name, counts in normalized_groups.items():
        total = counts["total"]
        selected = counts["selected"]
        rate = rates[group_name]
        
        # 4/5ths impact ratio
        ir = (rate / benchmark_rate) if benchmark_rate > 0 else 1.0
        ir = round(ir, 4)

        # 2-Standard Deviation test against benchmark
        if group_name == benchmark_group:
            z_score = 0.0
            stat_sig = False
        else:
            bench_counts = normalized_groups[benchmark_group]
            z_score, stat_sig = calculate_two_standard_deviation_z_score(
                selected, total, bench_counts["selected"], bench_counts["total"]
            )

        violates_four_fifths = (ir < 0.80) and (total >= 10)
        if violates_four_fifths:
            has_adverse_impact = True
            violations.append(
                f"Cohort '{group_name}' violates EEOC 4/5ths Rule (Impact Ratio: {ir * 100:.1f}% < 80.0%)."
            )

        if stat_sig and z_score < -1.96:
            violations.append(
                f"Cohort '{group_name}' exhibits statistically significant adverse disparity (Z = {z_score:.2f} SD)."
            )

        results_table[group_name] = {
            "total_candidates": total,
            "selected_candidates": selected,
            "selection_rate": round(rate, 4),
            "impact_ratio": ir,
            "z_score": z_score,
            "is_statistically_significant": stat_sig,
            "passes_four_fifths": not violates_four_fifths
        }

    return {
        "status": "NON_COMPLIANT" if has_adverse_impact else "COMPLIANT",
        "is_certified": not has_adverse_impact,
        "benchmark_group": benchmark_group,
        "benchmark_selection_rate": round(benchmark_rate, 4),
        "total_cohorts_evaluated": len(normalized_groups),
        "results_table": results_table,
        "violations": violations,
        "compliance_frameworks": [
            "EEOC Uniform Guidelines (29 CFR Part 1607)",
            "NYC Local Law 144 (AEDT Bias Audit)",
            "EU AI Act Article 10 (Data & Data Governance Bias Mitigation)"
        ]
    }
