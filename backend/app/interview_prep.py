import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from app.keywords import calculate_keyword_match_score

logger = logging.getLogger("InterviewPrepEngine")

# Configure Gemini API if key is present
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

INTERVIEW_PREP_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_readiness_score": {"type": "integer"},
        "readiness_tier": {"type": "string"},
        "summary_analysis": {"type": "string"},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "theme": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "recruiter_intent": {"type": "string"},
                    "question": {"type": "string"},
                    "star_strategy": {
                        "type": "object",
                        "properties": {
                            "situation": {"type": "string"},
                            "task": {"type": "string"},
                            "action": {"type": "string"},
                            "result": {"type": "string"}
                        },
                        "required": ["situation", "task", "action", "result"]
                    },
                    "pitfall_to_avoid": {"type": "string"}
                },
                "required": ["id", "theme", "difficulty", "recruiter_intent", "question", "star_strategy", "pitfall_to_avoid"]
            }
        }
    },
    "required": ["overall_readiness_score", "readiness_tier", "summary_analysis", "questions"]
}


def generate_fallback_interview_prep(
    resume_text: str,
    job_description: Optional[str] = None,
    seniority: str = "mid"
) -> Dict[str, Any]:
    """
    Deterministic rule-based interview preparation generator that runs
    locally when Gemini API is offline or unconfigured.
    """
    resume_lower = resume_text.lower() if resume_text else ""
    jd_lower = job_description.lower() if job_description else ""

    # Find missing keywords / gaps
    missing_tech = []
    common_eval_skills = ["kubernetes", "aws", "docker", "microservices", "kafka", "graphql", "ci/cd", "redis", "postgresql", "fastapi"]
    for tech in common_eval_skills:
        if jd_lower and tech in jd_lower and tech not in resume_lower:
            missing_tech.append(tech.title())

    if not missing_tech and jd_lower:
        kw_data = calculate_keyword_match_score(resume_text, job_description)
        missing_tech = kw_data.get("missing", [])[:3]

    if not missing_tech:
        missing_tech = ["Distributed Systems", "Cloud Scaling", "Observability"]

    # Detect unquantified bullets
    bullets = [line.strip() for line in resume_text.splitlines() if line.strip().startswith(('•', '-', '*', '–'))]
    unquantified = [b for b in bullets if not re.search(r'\d+(?:\.\d+)?%|\$\d+|\b\d+\b', b)]
    weak_bullet_sample = unquantified[0] if unquantified else "Led team development and improved architecture"

    questions = [
        {
            "id": 1,
            "theme": f"Tech Stack Alignment & Adjacent Tooling ({missing_tech[0] if missing_tech else 'Cloud Infrastructure'})",
            "difficulty": "Tough Technical",
            "recruiter_intent": f"The target job emphasizes {missing_tech[0] if missing_tech else 'modern cloud tooling'}, but your resume shows related experience rather than direct production tenure. They want to verify your ability to bridge this tooling gap without ramp-up friction.",
            "question": f"Our production stack relies heavily on {missing_tech[0] if missing_tech else 'distributed cloud architecture'}. Can you walk us through a time you had to deliver critical infrastructure using a technology you hadn't used in production before?",
            "star_strategy": {
                "situation": "Identify a past project where you successfully adopted a new framework, database, or cloud service under tight deadlines.",
                "task": "Highlight the business risk and the technical requirements that dictated using unfamiliar tooling.",
                "action": "Detail your ramp-up methodology: reading RFCs/source code, building rapid sandbox spikes, and implementing automated testing to ensure zero regressions.",
                "result": "State the launch outcome, on-time delivery, and ongoing operational stability of the service."
            },
            "pitfall_to_avoid": "Don't claim mastery if you haven't used it heavily. Emphasize fast architectural conceptual transfer and fundamental systems comprehension."
        },
        {
            "id": 2,
            "theme": "Metric Verification & Business Impact",
            "difficulty": "Probing Technical",
            "recruiter_intent": "Hiring managers probe lines with general claims to differentiate between engineers who merely executed tasks versus those who drove measurable business outcomes.",
            "question": f"On your resume, you mention: '{weak_bullet_sample[:90]}...'. How did you benchmark baseline performance before starting, and what were the exact before-and-after KPIs of that project?",
            "star_strategy": {
                "situation": "Provide specific numbers for team size, user volume, request throughput (QPS), or server costs associated with that project.",
                "task": "Explain the specific bottleneck or pain point that was hurting the business.",
                "action": "Walk through the architectural trade-offs: indexing optimizations, caching layers, or algorithmic refactoring you chose.",
                "result": "Quantify the outcome (e.g. 'Reduced P99 latency by 35% from 420ms to 270ms, saving $40k/yr in infrastructure')."
            },
            "pitfall_to_avoid": "Never say 'I don't remember the exact number.' Give reasonable approximations backed by engineering order-of-magnitude estimates (e.g. ~10k RPM, ~30% reduction)."
        },
        {
            "id": 3,
            "theme": "High-Severity Incident Management & Debugging",
            "difficulty": "System Design Drill",
            "recruiter_intent": "Evaluates your poise under pressure, post-mortem rigor, and whether you solve root causes rather than applying band-aids.",
            "question": "Tell me about the most critical production outage or data corruption issue you've caused or investigated. How did you triage it under pressure, and what invariant did you implement to prevent it from ever happening again?",
            "star_strategy": {
                "situation": "Choose an actual high-stakes outage (e.g. cascade connection pool exhaustion, memory leak, or misconfigured migration).",
                "task": "Explain the immediate business impact (e.g. checkout downtime, error rate spike) and time constraints.",
                "action": "Detail your structured root-cause triage: isolating telemetry logs, rolling back canary deployments, hotfixing, and conducting blameless post-mortems.",
                "result": "Describe the lasting architectural prevention mechanism added (e.g. circuit breakers, synthetic canary probes, automated load tests)."
            },
            "pitfall_to_avoid": "Don't blame teammates or junior devs. Senior engineers take extreme ownership and focus on systemic architectural safeguards."
        },
        {
            "id": 4,
            "theme": f"Seniority & Architectural Trade-offs ({seniority.title()} Scope)",
            "difficulty": "Architectural Drill",
            "recruiter_intent": f"For a {seniority.title()}-level role, interviewers look for technical maturity: understanding that every architecture choice has drawbacks and financial costs.",
            "question": "Describe a major technical decision or architectural pattern you advocated for that in hindsight proved to be the wrong choice. What trade-offs did you miscalculate, and how did you remediate it?",
            "star_strategy": {
                "situation": "Frame a decision made with the best available information at the time (e.g. premature microservices split, adopting an overly complex ORM/NoSQL schema).",
                "task": "Explain the unforeseen scaling bottlenecks, latency penalties, or developer velocity drag that emerged.",
                "action": "Demonstrate technical humility: how you recognized the inflection point, proposed pragmatic simplification, and led the refactor.",
                "result": "Highlight improved team velocity, reduced cloud bills, or reduced cognitive load across the engineering org."
            },
            "pitfall_to_avoid": "Don't pick a trivial non-mistake (e.g. 'I worked too hard'). Pick a real engineering trade-off that showcases your technical evolution."
        },
        {
            "id": 5,
            "theme": "Cross-Functional Friction & Scope Disagreements",
            "difficulty": "Behavioral Leadership",
            "recruiter_intent": "Probes how you navigate disagreements with Product Managers, Designers, or other Lead Engineers without stalling team momentum.",
            "question": "Can you share an experience where Product or Leadership demanded an aggressive deadline that you knew would compromise architectural integrity or introduce severe tech debt? How did you navigate the compromise?",
            "star_strategy": {
                "situation": "Describe a critical product launch with intense commercial or regulatory deadline pressure.",
                "task": "Explain the trade-off between speed-to-market and long-term architectural health.",
                "action": "Detail how you quantified tech debt in business terms, proposed an phased MVP delivery model, and scheduled dedicated debt paydown sprints.",
                "result": "Hit the critical business milestone on time without causing production outages, followed by planned stabilization."
            },
            "pitfall_to_avoid": "Avoid sounding stubborn or purely academic. Great engineers balance business urgency with pragmatic risk mitigation."
        }
    ]

    return {
        "overall_readiness_score": 88,
        "readiness_tier": "High Interview Preparedness",
        "summary_analysis": f"Identified {len(questions)} key vulnerability probe vectors based on your resume profile and target {seniority.title()} engineering tier. Focus your prep on quantifying unmeasured bullet points and bridging the {missing_tech[0]} tooling gap.",
        "questions": questions
    }


async def generate_interview_prep(
    resume_text: str,
    job_description: Optional[str] = None,
    seniority: Optional[str] = "mid"
) -> Dict[str, Any]:
    """
    Generates tailored interview preparation questions and STAR strategies using
    Gemini 1.5 Flash structured outputs when available, falling back to deterministic heuristics.
    """
    if not resume_text or len(resume_text.strip()) < 10:
        return {
            "overall_readiness_score": 0,
            "readiness_tier": "No Content",
            "summary_analysis": "Please provide your resume text to generate targeted interview questions.",
            "questions": []
        }

    sen_level = seniority or "mid"

    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": INTERVIEW_PREP_SCHEMA,
                    "temperature": 0.2
                }
            )

            prompt = f"""
You are a Principal Engineering Interviewer and FAANG Hiring Committee Member.
Analyze the following candidate resume against the target role requirements and seniority level ({sen_level}).

Identify the TOP 5 most difficult, probing interview questions a hiring manager or tech lead will grill this candidate on based on:
1. Gaps between resume skills and target Job Description.
2. Vague or unquantified resume bullet points.
3. Architecture, scaling, and system design complexity appropriate for {sen_level} tier.
4. Past incident debugging, trade-offs, and root-cause post-mortems.
5. Technical disagreements and engineering leadership under deadline pressure.

For each question, provide:
- The hidden recruiter intent / concern being evaluated.
- The exact tough, realistic question.
- A step-by-step STAR strategy (Situation, Task, Action, Result) calibrated to the candidate's actual projects.
- A key pitfall to avoid.

Target Seniority: {sen_level}
Target Job Description:
{job_description or "General Senior Full Stack / Backend Engineering Role"}

Candidate Resume:
{resume_text}
"""
            response = await model.generate_content_async(prompt)
            if response.text:
                data = json.loads(response.text)
                return data
        except Exception as e:
            logger.warning(f"Gemini Interview Prep generation failed, using heuristic fallback: {e}")

    # Deterministic Heuristic Fallback
    return generate_fallback_interview_prep(resume_text, job_description, sen_level)
