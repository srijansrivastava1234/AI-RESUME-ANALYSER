import re
from typing import Dict, Any, List, Optional
from app.xyz_scorer import score_resume_bullet, DUTY_STATEMENT_PATTERNS

# Seniority targets calibrated per ATS Validator Architect standards
SENIORITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "junior": {
        "title": "Junior / Entry-Level (0–2 years)",
        "target_xyz_ratio": 0.70,
        "target_strategic_ratio": 0.30,
        "focus": "Task execution, velocity, and foundational stack mastery.",
        "expected_leadership_weight": 0.10,
    },
    "mid": {
        "title": "Mid-Level Engineer (3–5 years)",
        "target_xyz_ratio": 0.80,
        "target_strategic_ratio": 0.20,
        "focus": "Feature ownership, optimization, throughput, and autonomous delivery.",
        "expected_leadership_weight": 0.20,
    },
    "senior": {
        "title": "Senior Engineer (6–9 years)",
        "target_xyz_ratio": 0.85,
        "target_strategic_ratio": 0.15,
        "focus": "System architecture, latency reduction, cost savings, mentoring, and scale.",
        "expected_leadership_weight": 0.35,
    },
    "staff": {
        "title": "Staff / Principal Engineer (10+ years)",
        "target_xyz_ratio": 0.60,
        "target_strategic_ratio": 0.40,
        "focus": "Cross-org initiatives, architectural standards, technical vision, and strategic roadmaps.",
        "expected_leadership_weight": 0.60,
    },
    "executive": {
        "title": "Executive / VP / Director (15+ years)",
        "target_xyz_ratio": 0.50,
        "target_strategic_ratio": 0.50,
        "focus": "P&L ownership, organizational design, governance, and enterprise risk mitigation.",
        "expected_leadership_weight": 0.80,
    },
}

STRATEGIC_KEYWORDS = {
    "architecture", "architectural", "governance", "p&l", "budget", "mentored",
    "mentoring", "cross-functional", "cross-org", "standardized", "standards",
    "roadmap", "strategic", "organizational", "retention", "compliance",
    "stakeholders", "executive", "board", "transformation", "charter",
    "initiative", "hiring", "headcount", "strategy", "vision", "spearheaded"
}


def audit_seniority_distribution(
    bullets: List[str],
    target_tier: str = "senior"
) -> Dict[str, Any]:
    """
    Audits the ratio of quantifiable Google/IBM X-Y-Z bullets versus contextual/strategic narrative,
    calibrated against the candidate's target seniority tier.

    :param bullets: List of resume achievement bullet points
    :param target_tier: Target seniority ('junior', 'mid', 'senior', 'staff', 'executive')
    :return: Seniority alignment scorecard, actual vs target ratios, and actionable recommendations
    """
    clean_tier = (target_tier or "senior").lower().strip()
    profile = SENIORITY_PROFILES.get(clean_tier, SENIORITY_PROFILES["senior"])

    clean_bullets = [b.strip() for b in bullets if b and b.strip()]
    total_bullets = len(clean_bullets)

    if total_bullets == 0:
        return {
            "target_tier": clean_tier,
            "tier_title": profile["title"],
            "total_bullets": 0,
            "seniority_alignment_index": 0,
            "alignment_grade": "D",
            "target_xyz_ratio": profile["target_xyz_ratio"],
            "actual_xyz_ratio": 0.0,
            "target_strategic_ratio": profile["target_strategic_ratio"],
            "actual_strategic_ratio": 0.0,
            "duty_ratio": 0.0,
            "quantified_count": 0,
            "strategic_count": 0,
            "duty_count": 0,
            "bullet_breakdowns": [],
            "recommendations": [
                "No bullets provided. Add achievement statements to evaluate seniority alignment."
            ],
            "strategic_focus": profile["focus"]
        }

    xyz_count = 0
    strategic_count = 0
    duty_count = 0
    bullet_breakdowns = []

    for b in clean_bullets:
        score_data = score_resume_bullet(b, seniority=clean_tier)
        detected_metrics = score_data.get("detected_metrics", [])
        has_metric = len(detected_metrics) > 0
        penalties = score_data.get("penalties", [])
        is_duty = any(
            p.get("name") == "Passive Duty Statement" or "passive" in p.get("reason", "").lower()
            for p in penalties
        )

        # Check strategic narrative indicators
        words = set(re.findall(r'\b[a-zA-Z\-]+\b', b.lower()))
        matched_strategic = words.intersection(STRATEGIC_KEYWORDS)
        is_strategic = len(matched_strategic) > 0

        if is_duty:
            duty_count += 1
            classification = "Passive Duty Phrasing"
        elif has_metric and is_strategic:
            xyz_count += 1
            strategic_count += 1
            classification = "Strategic Quantified Impact"
        elif has_metric:
            xyz_count += 1
            classification = "Quantified X-Y-Z Impact"
        elif is_strategic:
            strategic_count += 1
            classification = "Strategic / Systemic Narrative"
        else:
            classification = "Contextual Statement"

        bullet_breakdowns.append({
            "bullet": b,
            "score": score_data.get("score", 0),
            "classification": classification,
            "has_metric": has_metric,
            "detected_metrics": detected_metrics,
            "is_duty": is_duty,
            "is_strategic": is_strategic,
            "matched_strategic_terms": sorted(list(matched_strategic))
        })

    actual_xyz_ratio = round(xyz_count / total_bullets, 2)
    actual_strategic_ratio = round(strategic_count / total_bullets, 2)
    duty_ratio = round(duty_count / total_bullets, 2)

    # Compute Seniority Alignment Index (0 to 100)
    target_xyz = profile["target_xyz_ratio"]
    target_strat = profile["target_strategic_ratio"]

    xyz_delta = abs(actual_xyz_ratio - target_xyz)
    strat_delta = abs(actual_strategic_ratio - target_strat)

    base_penalty = (xyz_delta * 45.0) + (duty_ratio * 40.0)

    # For Staff/Exec, penalize missing strategic leadership
    if clean_tier in ("staff", "executive") and actual_strategic_ratio < target_strat:
        base_penalty += strat_delta * 30.0

    raw_score = 100.0 - base_penalty
    alignment_score = max(0, min(100, int(round(raw_score))))

    # Determine Grade
    if alignment_score >= 90:
        grade = "A+"
    elif alignment_score >= 80:
        grade = "A"
    elif alignment_score >= 70:
        grade = "B"
    elif alignment_score >= 55:
        grade = "C"
    else:
        grade = "D"

    recommendations = []
    if duty_count > 0:
        recommendations.append(
            f"Eliminate passive phrasing in {duty_count} bullet(s) (e.g., replace 'Responsible for' with active impact verbs like 'Architected' or 'Engineered')."
        )

    if actual_xyz_ratio < target_xyz:
        gap_pct = int(round((target_xyz - actual_xyz_ratio) * 100))
        recommendations.append(
            f"Under-indexing on quantifiable metrics by {gap_pct}%. For a {clean_tier.capitalize()} profile, anchor {int(target_xyz*100)}% of bullets with hard metrics ($, %, ms, scale)."
        )
    elif actual_xyz_ratio > target_xyz + 0.15 and clean_tier in ("staff", "executive"):
        recommendations.append(
            f"Over-indexing on purely task-level metrics ({int(actual_xyz_ratio*100)}% vs target {int(target_xyz*100)}%). Incorporate systemic and cross-organizational narrative (standards, vision, governance)."
        )

    if clean_tier in ("staff", "executive") and actual_strategic_ratio < target_strat:
        recommendations.append(
            f"Strategic scope is below target ({int(actual_strategic_ratio*100)}% vs target {int(target_strat*100)}%). Highlight cross-org standards, roadmaps, or P&L responsibilities."
        )

    if not recommendations:
        recommendations.append(
            f"Optimal bullet distribution achieved for {profile['title']}. Strong balance of quantifiable impact and strategic scope."
        )

    return {
        "target_tier": clean_tier,
        "tier_title": profile["title"],
        "total_bullets": total_bullets,
        "seniority_alignment_index": alignment_score,
        "alignment_grade": grade,
        "target_xyz_ratio": target_xyz,
        "actual_xyz_ratio": actual_xyz_ratio,
        "target_strategic_ratio": target_strat,
        "actual_strategic_ratio": actual_strategic_ratio,
        "duty_ratio": duty_ratio,
        "quantified_count": xyz_count,
        "strategic_count": strategic_count,
        "duty_count": duty_count,
        "bullet_breakdowns": bullet_breakdowns,
        "recommendations": recommendations,
        "strategic_focus": profile["focus"]
    }
