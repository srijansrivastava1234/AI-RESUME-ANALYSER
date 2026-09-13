"""
Agent-Native BYOK (Bring-Your-Own-Key) Prompt Synthesis Engine.

Generates structured, zero-hallucination refactoring prompts for external LLMs
(Claude 3.5 Sonnet, GPT-4o, Cursor) adhering to ATS Validator Architecture:
- Strict Anti-Fabrication Rule (Zero Hallucination of metrics or skills)
- Google/IBM X-Y-Z formulation ('Accomplished [X], measured by [Y], by doing [Z]')
- Seniority-calibrated ratio enforcement
- Verifiable Gap classification
"""

from typing import Dict, Any, List, Optional
from app.compliance import extract_resume_bullets
from app.xyz_scorer import score_resume_bullet


def generate_agent_refactor_prompt(
    resume_text: str,
    job_description: Optional[str] = None,
    target_seniority: str = "mid",
    missing_keywords: Optional[List[str]] = None,
    identified_weak_bullets: Optional[List[str]] = None
) -> str:
    """
    Synthesizes a production-grade Agent-Native markdown prompt configured
    for external frontier LLMs (Claude 3.5 Sonnet, ChatGPT GPT-4o, Cursor).

    :param resume_text: Raw candidate resume text
    :param job_description: Target job description
    :param target_seniority: Seniority level (junior, mid, senior, staff, executive)
    :param missing_keywords: List of missing technical competencies
    :param identified_weak_bullets: List of weak/passive duty bullets needing rewrite
    :return: Formatted markdown prompt ready for one-click clipboard copy
    """
    seniority = target_seniority.capitalize()

    # Automatically extract weak bullets if not explicitly supplied
    if identified_weak_bullets is None:
        extracted = extract_resume_bullets(resume_text)
        weak = []
        for b in extracted:
            audit = score_resume_bullet(b, seniority=target_seniority)
            if audit["score"] < 70:
                weak.append(b)
        identified_weak_bullets = weak[:5]  # Limit to top 5 weak bullets

    bullets_section = "\n".join([f"- \"{b}\"" for b in identified_weak_bullets]) if identified_weak_bullets else "- [All existing bullets achieved >= 70 XYZ threshold. Provide candidate bullets to optimize.]"

    keywords_section = ", ".join(missing_keywords) if missing_keywords else "None identified (Maintain technical keyword density)"
    jd_section = job_description.strip() if job_description and job_description.strip() else "Targeting modern engineering standards for this seniority level."

    prompt = f"""# ROLE: SENIOR TECHNICAL RESUME ARCHITECT & ATS COMPLIANCE SPECIALIST

You are acting as an elite career dossier editor and ATS compliance auditor.
Your mission is to rewrite the candidate's weak resume bullet points using strictly the **Google/IBM X-Y-Z Accomplishment Formula**:
> **"Accomplished [X] as measured by [Y], by doing [Z]"**

Calibrate your rewrites specifically for a **{seniority}** seniority level.

---

## 🎯 TARGET JOB REQUIREMENTS
{jd_section}

---

## 🔍 IDENTIFIED COMPETENCY GAPS (Incorporate ONLY if verified by candidate context)
{keywords_section}

---

## ⚠️ BULLETS REQUIRING REFACTORING
{bullets_section}

---

## 🚨 STRICT EDITORIAL RULES (ANTI-FABRICATION SAFEGUARD)
1. **ZERO FABRICATION**: Never invent tools, metrics, percentages, dollar amounts, employer names, or credentials not supported by candidate background. If a metric is unknown, insert a bracketed placeholder like `[reduced latency by X% / by Y ms]`.
2. **ACTIVE PAST-TENSE VERBS**: Begin every bullet with a strong Bloom's taxonomy action verb (e.g. Architected, Engineered, Spearheaded, Orchestrated, Automated, Optimized). Avoid passive duty phrases ("Responsible for", "Helped with").
3. **FRONT-LOAD IMPACT (The First-Third Rule)**: Recruiters scan resumes in 6 to 7.4 seconds. State the high-impact outcome first, followed by the technical methodology and stack.
4. **COGNITIVE LOAD CEILING**: Keep every refactored bullet between **18 and 28 words**. Bullets over 30 words cause recruiter skim fatigue.
5. **OUTPUT FORMAT**: Return ONLY the refactored bullets in Markdown format with a brief 1-line rationale for each change.
"""
    return prompt.strip()


def generate_byok_export_package(
    resume_text: str,
    compliance_report: Dict[str, Any],
    job_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Assembles a complete Bring-Your-Own-Key (BYOK) export package.
    Includes the deterministic compliance scorecard, regulatory safe harbor status,
    and copy-ready agent prompt.
    """
    missing_kws = compliance_report.get("pillars", {}).get("keywords", {}).get("missing_keywords", [])
    seniority = compliance_report.get("target_seniority", "mid")

    agent_prompt = generate_agent_refactor_prompt(
        resume_text=resume_text,
        job_description=job_description,
        target_seniority=seniority,
        missing_keywords=missing_kws
    )

    return {
        "metadata": {
            "engine": "ATS Resume Analyser AI (BYOK Native)",
            "version": "1.6.0",
            "compliance_grade": compliance_report.get("letter_grade"),
            "composite_score": compliance_report.get("composite_score"),
            "target_seniority": seniority,
            "target_pages": compliance_report.get("target_pages", 1)
        },
        "scorecard": compliance_report,
        "agent_refactor_prompt": agent_prompt,
        "regulatory_safe_harbor": compliance_report.get("regulatory_safe_harbor", {})
    }
