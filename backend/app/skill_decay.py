"""
Exponential Half-Life Skill Decay & Freshness Profiler.
Models currency and obsolescence of technical skills across a candidate's career timeline
using parameterized exponential half-life decay curves calibrated by technology domain.
"""

import re
import math
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Domain half-life configurations (in years)
DOMAIN_HALF_LIVES = {
    "rapid_moving": 2.5,   # Frontend frameworks, AI/ML libraries, Cloud SDKs
    "standard_tech": 4.0,  # Backend languages, Databases, Container orchestration
    "evergreen": 8.0       # SQL, Algorithms, Linux, Networking, Operating Systems
}

SKILL_DOMAIN_MAP = {
    # Rapid-moving (2.5 years half-life)
    "react": "rapid_moving",
    "next.js": "rapid_moving",
    "vue": "rapid_moving",
    "angular": "rapid_moving",
    "tailwind": "rapid_moving",
    "langchain": "rapid_moving",
    "llamaindex": "rapid_moving",
    "pytorch": "rapid_moving",
    "tensorflow": "rapid_moving",
    "transformers": "rapid_moving",
    "fastapi": "rapid_moving",
    "graphql": "rapid_moving",
    "svelte": "rapid_moving",
    "vite": "rapid_moving",
    "huggingface": "rapid_moving",

    # Standard (4.0 years half-life)
    "python": "standard_tech",
    "golang": "standard_tech",
    "rust": "standard_tech",
    "java": "standard_tech",
    "node.js": "standard_tech",
    "nodejs": "standard_tech",
    "c#": "standard_tech",
    "c++": "standard_tech",
    "docker": "standard_tech",
    "kubernetes": "standard_tech",
    "postgresql": "standard_tech",
    "mongodb": "standard_tech",
    "redis": "standard_tech",
    "aws": "standard_tech",
    "gcp": "standard_tech",
    "azure": "standard_tech",
    "kafka": "standard_tech",
    "django": "standard_tech",
    "flask": "standard_tech",

    # Evergreen (8.0 years half-life)
    "sql": "evergreen",
    "linux": "evergreen",
    "bash": "evergreen",
    "git": "evergreen",
    "algorithms": "evergreen",
    "data structures": "evergreen",
    "rest": "evergreen",
    "microservices": "evergreen",
    "ci/cd": "evergreen",
    "distributed systems": "evergreen",
}

YEAR_PATTERN = re.compile(r"\b(20\d\d|19\d\d)\b")

def calculate_skill_decay_score(years_since_active: float, domain: str) -> float:
    """
    Computes S(t) = S0 * exp(-lambda * t) where lambda = ln(2) / half_life.
    Returns retention percentage between 0 and 100.
    """
    half_life = DOMAIN_HALF_LIVES.get(domain, 4.0)
    decay_constant = math.log(2) / half_life
    retention = 100.0 * math.exp(-decay_constant * max(0.0, years_since_active))
    return round(min(100.0, max(0.0, retention)), 1)

def profile_skill_decay(
    resume_text: str,
    reference_year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Profiles technical skill freshness and obsolescence risk across resume text.
    """
    if reference_year is None:
        reference_year = datetime.datetime.now().year

    if not resume_text or not resume_text.strip():
        return {
            "freshness_index": 100.0,
            "grade": "A+",
            "skills_profiled": 0,
            "active_skills": [],
            "decaying_skills": [],
            "dormant_skills": [],
            "recommendations": []
        }

    # Identify all years in text to establish max recent activity
    years_found = [int(y) for y in YEAR_PATTERN.findall(resume_text) if 1990 <= int(y) <= reference_year + 1]
    latest_year_in_resume = max(years_found) if years_found else reference_year

    # Extract skill mentions and associate with context recency
    lower_text = resume_text.lower()
    profiled_skills = []

    for skill, domain in SKILL_DOMAIN_MAP.items():
        # Match whole word
        pattern = re.compile(r"\b" + re.escape(skill) + r"\b", re.IGNORECASE)
        match = pattern.search(lower_text)
        if match:
            # Check proximity to year in same paragraph/section
            snippet_start = max(0, match.start() - 150)
            snippet_end = min(len(lower_text), match.end() + 150)
            snippet = lower_text[snippet_start:snippet_end]
            local_years = [int(y) for y in YEAR_PATTERN.findall(snippet) if 1990 <= int(y) <= reference_year + 1]

            if local_years:
                skill_last_year = max(local_years)
            else:
                skill_last_year = latest_year_in_resume

            years_elapsed = max(0.0, float(reference_year - skill_last_year))
            retention_score = calculate_skill_decay_score(years_elapsed, domain)

            status = "active"
            if retention_score < 40.0:
                status = "dormant"
            elif retention_score < 75.0:
                status = "decaying"

            profiled_skills.append({
                "skill": skill.capitalize() if len(skill) > 3 else skill.upper(),
                "domain": domain,
                "last_active_year": skill_last_year,
                "years_inactive": round(years_elapsed, 1),
                "retention_score": retention_score,
                "status": status
            })

    if not profiled_skills:
        return {
            "freshness_index": 85.0,
            "grade": "B+",
            "skills_profiled": 0,
            "active_skills": [],
            "decaying_skills": [],
            "dormant_skills": [],
            "recommendations": ["Include standardized technical skills to enable tech stack freshness auditing."]
        }

    avg_score = sum(s["retention_score"] for s in profiled_skills) / len(profiled_skills)
    freshness_index = round(avg_score, 1)

    if freshness_index >= 90:
        grade = "A+"
    elif freshness_index >= 80:
        grade = "A"
    elif freshness_index >= 70:
        grade = "B"
    elif freshness_index >= 60:
        grade = "C"
    else:
        grade = "D"

    active_skills = [s for s in profiled_skills if s["status"] == "active"]
    decaying_skills = [s for s in profiled_skills if s["status"] == "decaying"]
    dormant_skills = [s for s in profiled_skills if s["status"] == "dormant"]

    recommendations = []
    if dormant_skills:
        dormant_names = ", ".join(d["skill"] for d in dormant_skills[:3])
        recommendations.append(
            f"Dormant skills detected ({dormant_names}): Skills inactive > 4+ years risk ATS discounting. Pair with recent hands-on projects."
        )
    if decaying_skills:
        decaying_names = ", ".join(d["skill"] for d in decaying_skills[:3])
        recommendations.append(
            f"Transitioning skills ({decaying_names}): Highlight ongoing production use or modern architectural context."
        )
    if not recommendations:
        recommendations.append("High technical freshness: Key skills show recent production activity across active roles.")

    return {
        "freshness_index": freshness_index,
        "grade": grade,
        "skills_profiled": len(profiled_skills),
        "active_skills": active_skills,
        "decaying_skills": decaying_skills,
        "dormant_skills": dormant_skills,
        "recommendations": recommendations
    }
