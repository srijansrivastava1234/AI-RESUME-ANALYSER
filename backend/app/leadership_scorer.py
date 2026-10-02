"""Leadership Trajectory & Organizational Scope Profiler.

Evaluates resume text across 5 leadership dimensions:
1. People Management & Mentorship
2. Architectural & Technical Governance
3. Cross-Functional Stakeholder Alignment
4. Budget, P&L & Resource Stewardship
5. Innovation, Open Source & Industry Thought Leadership

Maps candidate scope to seniority tiers (IC, Tech Lead, Staff+, Engineering Manager, Director/VP).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


LEADERSHIP_DIMENSIONS = {
    "PEOPLE_MANAGEMENT": {
        "label": "People Management & Mentorship",
        "weight": 0.25,
        "patterns": [
            re.compile(r"\b(?:managed|led|mentored|coached|guided|supervis(?:ed|ing)|hiring manager|onboarded|conducted \d+ interviews|team of \d+)\b", re.IGNORECASE),
            re.compile(r"\b(?:direct reports?|people manager|1-on-1s?|performance reviews?|career development)\b", re.IGNORECASE),
        ],
    },
    "TECHNICAL_GOVERNANCE": {
        "label": "Architectural & Technical Governance",
        "weight": 0.25,
        "patterns": [
            re.compile(r"\b(?:architected|technical roadmap|RFC author|system design|tech lead|governance|engineering standards|code review standards)\b", re.IGNORECASE),
            re.compile(r"\b(?:platform vision|technology strategy|evaluated vendors|decided tech stack|principal engineer)\b", re.IGNORECASE),
        ],
    },
    "STAKEHOLDER_ALIGNMENT": {
        "label": "Cross-Functional Stakeholder Alignment",
        "weight": 0.20,
        "patterns": [
            re.compile(r"\b(?:partnered with|collaborated with (?:product|design|sales|marketing|executives|c-suite|legal)|presented to executives|board meetings?)\b", re.IGNORECASE),
            re.compile(r"\b(?:cross-functional|stakeholder alignment|business requirements|client-facing|customer escalations)\b", re.IGNORECASE),
        ],
    },
    "RESOURCE_STEWARDSHIP": {
        "label": "Budget, P&L & Resource Stewardship",
        "weight": 0.15,
        "patterns": [
            re.compile(r"\b(?:budget|cost reduction|capex|opex|\$\s*\d+[\d,]*\s*(?:k|m|million|thousand)|cloud spend|finops|procurement|contract negotiation)\b", re.IGNORECASE),
            re.compile(r"\b(?:allocated resources|headcount planning|roi|p&l)\b", re.IGNORECASE),
        ],
    },
    "INNOVATION_THOUGHT_LEADERSHIP": {
        "label": "Innovation & Thought Leadership",
        "weight": 0.15,
        "patterns": [
            re.compile(r"\b(?:patents?|published paper|keynote speaker|conference speaker|open source maintainer|author|tech talk|whitepaper)\b", re.IGNORECASE),
            re.compile(r"\b(?:industry standards|inventor|hackathon winner|advisory board)\b", re.IGNORECASE),
        ],
    },
}


def profile_leadership_trajectory(text: str) -> Dict[str, Any]:
    """Profiles leadership competencies and organizational scope.

    Args:
        text: Raw resume plain text.

    Returns:
        Dict containing:
            - overall_leadership_score: float (0.0 to 100.0)
            - inferred_leadership_tier: str ("IC", "TECH_LEAD", "STAFF_PLUS", "ENGINEERING_MANAGER", "DIRECTOR_VP")
            - dimension_scores: Dict[str, Dict]
            - evidence_snippets: List[str]
            - recommendations: List[str]
    """
    if not text or not text.strip():
        return {
            "overall_leadership_score": 0.0,
            "inferred_leadership_tier": "INDIVIDUAL_CONTRIBUTOR",
            "dimension_scores": {},
            "evidence_snippets": [],
            "recommendations": ["No text provided for leadership trajectory profiling."],
        }

    dimension_results: Dict[str, Any] = {}
    total_weighted_score = 0.0
    all_evidence: List[str] = []

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for dim_key, dim_info in LEADERSHIP_DIMENSIONS.items():
        matched_count = 0
        dim_evidence: List[str] = []

        for line in lines:
            line_has_dim = False
            for pat in dim_info["patterns"]:
                matches = pat.findall(line)
                if matches:
                    matched_count += len(matches)
                    line_has_dim = True
            if line_has_dim:
                snippet = line if len(line) <= 100 else line[:97] + "..."
                if snippet not in dim_evidence:
                    dim_evidence.append(snippet)
                if snippet not in all_evidence:
                    all_evidence.append(snippet)

        # Raw score for dimension (0 to 100) based on hits (1 hit = 65, 2 hits = 85, 3+ hits = 100)
        if matched_count == 0:
            dim_score = 0.0
        elif matched_count == 1:
            dim_score = 65.0
        elif matched_count == 2:
            dim_score = 85.0
        else:
            dim_score = 100.0

        weighted_pts = dim_score * dim_info["weight"]
        total_weighted_score += weighted_pts

        dimension_results[dim_key] = {
            "label": dim_info["label"],
            "score": round(dim_score, 1),
            "weight": dim_info["weight"],
            "matches_count": matched_count,
            "evidence": dim_evidence[:3],
        }

    active_dims = sum(1 for d in dimension_results.values() if d["score"] > 0)
    breadth_bonus = 15.0 if active_dims >= 4 else (8.0 if active_dims >= 3 else 0.0)
    final_score = max(0.0, min(100.0, round(total_weighted_score + breadth_bonus, 1)))

    # Inferred Leadership Tier
    if final_score >= 80.0:
        tier = "DIRECTOR_OR_VP"
    elif final_score >= 65.0:
        tier = "STAFF_PRINCIPAL_OR_ENGINEERING_MANAGER"
    elif final_score >= 45.0:
        tier = "TECH_LEAD_OR_LEAD_ENGINEER"
    elif final_score >= 20.0:
        tier = "SENIOR_INDIVIDUAL_CONTRIBUTOR"
    else:
        tier = "INDIVIDUAL_CONTRIBUTOR"

    # Actionable Recommendations
    recommendations: List[str] = []
    if dimension_results["PEOPLE_MANAGEMENT"]["score"] < 40.0:
        recommendations.append(
            "Highlight mentorship and team enablement (e.g. 'Mentored 3 junior engineers and onboarded new team hires')."
        )
    if dimension_results["TECHNICAL_GOVERNANCE"]["score"] < 40.0:
        recommendations.append(
            "Emphasize technical decision ownership, RFC authorship, and architectural roadmap leadership."
        )
    if dimension_results["STAKEHOLDER_ALIGNMENT"]["score"] < 40.0:
        recommendations.append(
            "Showcase cross-functional impact partnering with Product, Design, Sales, or Executive stakeholders."
        )
    if not recommendations:
        recommendations.append(
            "Strong leadership scope and high-impact cross-functional signals demonstrated throughout the resume."
        )

    return {
        "overall_leadership_score": final_score,
        "inferred_leadership_tier": tier,
        "dimension_scores": dimension_results,
        "evidence_snippets": all_evidence[:6],
        "recommendations": recommendations,
    }
