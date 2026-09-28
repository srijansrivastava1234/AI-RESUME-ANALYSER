"""
Resume Buzzword and Corporate Jargon Density Analyzer.
Evaluates resumes for overused buzzwords, fluff phrases, and corporate clichés,
providing replacement suggestions grounded in the Google X-Y-Z formula.
"""

import re
from typing import Dict, Any, List, Set

CORPORATE_BUZZWORDS = {
    "synergy": "cross-functional collaboration / aligned architecture",
    "thought leader": "domain expert / author / technical lead",
    "paradigm shift": "architectural transition / fundamental restructuring",
    "game changer": "high-impact initiative / key performance milestone",
    "rockstar": "senior engineer / top-tier performer",
    "ninja": "specialist / senior developer",
    "guru": "subject matter expert / technical specialist",
    "out of the box": "innovative / custom-engineered",
    "out-of-the-box": "innovative / custom-engineered",
    "deep dive": "comprehensive analysis / architectural audit",
    "move the needle": "quantifiably increased revenue / reduced latency",
    "circle back": "follow up / synchronized review",
    "bandwidth": "capacity / availability",
    "low hanging fruit": "immediate optimizations / quick wins",
    "results-driven": "demonstrated track record with quantified outcomes",
    "results driven": "demonstrated track record with quantified outcomes",
    "self-starter": "autonomous contributor / initiated and led",
    "self starter": "autonomous contributor / initiated and led",
    "team player": "collaborative contributor / cross-team partner",
    "hard worker": "dedicated engineer / proven track record",
    "go-getter": "proactive lead / initiative driver",
    "go getter": "proactive lead / initiative driver",
    "leverage": "utilized / implemented / deployed",
    "hit the ground running": "rapidly onboarded / delivered within sprint 1",
    "dynamic": "adaptable / multifaceted",
    "detail-oriented": "precise / rigorous in QA and testing",
    "detail oriented": "precise / rigorous in QA and testing",
}


def audit_buzzword_density(resume_text: str) -> Dict[str, Any]:
    """
    Audits resume text for buzzword density, corporate clichés, and empty fluff terms.

    Returns:
        Dict containing:
        - buzzword_count: Total occurrences
        - unique_buzzwords: List of distinct detected buzzwords
        - jargon_density_pct: Percentage of total words that are buzzwords
        - buzzword_free_score: 0-100 score (100 = completely clean, objective tone)
        - detected_instances: List of matches with line context and suggested replacements
        - recommendations: Actionable improvement suggestions
    """
    if not resume_text or not resume_text.strip():
        return {
            "buzzword_count": 0,
            "unique_buzzwords": [],
            "jargon_density_pct": 0.0,
            "buzzword_free_score": 100.0,
            "detected_instances": [],
            "recommendations": ["No text provided for buzzword analysis."]
        }

    words = re.findall(r"\b\w+\b", resume_text)
    total_words = max(1, len(words))
    resume_lower = resume_text.lower()

    detected_instances: List[Dict[str, str]] = []
    unique_buzzwords: Set[str] = set()
    total_count = 0

    for buzzword, suggestion in sorted(CORPORATE_BUZZWORDS.items(), key=lambda x: -len(x[0])):
        pattern = r"\b" + re.escape(buzzword) + r"\b"
        matches = list(re.finditer(pattern, resume_lower))
        if matches:
            total_count += len(matches)
            unique_buzzwords.add(buzzword)
            for m in matches:
                start = max(0, m.start() - 30)
                end = min(len(resume_text), m.end() + 30)
                snippet = resume_text[start:end].replace("\n", " ").strip()
                detected_instances.append({
                    "buzzword": buzzword,
                    "context": f"...{snippet}...",
                    "suggested_replacement": suggestion
                })

    density_pct = round((total_count / total_words) * 100.0, 2)
    # Deduct 5 points per buzzword instance, down to minimum 0
    clean_score = max(0.0, round(100.0 - (total_count * 5.0), 1))

    recommendations: List[str] = []
    if total_count == 0:
        recommendations.append("Excellent! No corporate buzzwords or vague fluff terms detected.")
    elif total_count <= 2:
        recommendations.append(
            f"Found {total_count} corporate buzzword(s). Replace vague terms with quantifiable Google X-Y-Z achievements."
        )
    else:
        recommendations.append(
            f"High buzzword density detected ({total_count} instances, {density_pct}% of text). "
            f"Replace vague phrases like '{list(unique_buzzwords)[0]}' with direct metrics, technical tools, and quantified outcomes."
        )

    return {
        "buzzword_count": total_count,
        "unique_buzzwords": sorted(list(unique_buzzwords)),
        "jargon_density_pct": density_pct,
        "buzzword_free_score": clean_score,
        "detected_instances": detected_instances[:15],
        "recommendations": recommendations
    }
