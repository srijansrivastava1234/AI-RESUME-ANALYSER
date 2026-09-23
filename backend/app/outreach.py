"""
Module: outreach.py
Purpose: Synthesizes high-converting, tailored job application outreach copy
(Cover Letters, LinkedIn InMails, Hiring Manager Cold Emails, and Follow-Up Notes)
grounded directly in candidate resume achievements and target JD requirements.
"""

import re
import os
import json
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Fallback templates for deterministic generation
def _extract_key_accomplishments(resume_text: str) -> List[str]:
    """Finds strong accomplishment bullets containing metrics or percentages."""
    metric_regex = re.compile(r'(\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b)?|\b\d+\+?\s+(?:users|customers|engineers|services|qps|events|ms|latency|hours)\b)', re.I)
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    bullets = []
    
    for line in lines:
        cleaned = re.sub(r'^[•\-\*\u2022\u25cf\d\.]+\s*', '', line).strip()
        if len(cleaned) > 25 and metric_regex.search(cleaned):
            bullets.append(cleaned)
            if len(bullets) >= 3:
                break

    if not bullets and lines:
        for line in lines:
            cleaned = re.sub(r'^[•\-\*\u2022\u25cf\d\.]+\s*', '', line).strip()
            if len(cleaned) > 30 and len(cleaned.split()) > 5:
                bullets.append(cleaned)
                if len(bullets) >= 2:
                    break

    return bullets or [
        "Architected scalable cloud systems delivering 40% performance improvements.",
        "Engineered robust production pipelines reducing deployment friction."
    ]


def _extract_candidate_identity(resume_text: str) -> Dict[str, str]:
    """Extracts candidate name and primary role title."""
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    name = "Candidate"
    email = ""
    
    if lines:
        first = lines[0]
        if len(first) < 40 and not '@' in first and not any(k in first.lower() for k in ['resume', 'curriculum', 'summary']):
            name = first.title()

    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    if email_match:
        email = email_match.group(0)

    return {"name": name, "email": email}


def _extract_target_context(job_desc: str, company_name: Optional[str] = None, recipient_name: Optional[str] = None) -> Dict[str, str]:
    """Extracts target company and job title from JD or inputs."""
    target_company = company_name or "your team"
    target_role = "Target Position"
    rec_name = recipient_name or "Hiring Team"

    if job_desc:
        title_match = re.search(r'(?:job\s+title|role|position|hiring\s+for):\s*([^\n\r]+)', job_desc, re.I)
        if title_match:
            target_role = title_match.group(1).strip()
        else:
            # Check first line for title-like words
            first_line = job_desc.split('\n')[0].strip()
            if len(first_line) < 50 and any(w in first_line.lower() for w in ['engineer', 'developer', 'manager', 'lead', 'architect', 'analyst', 'designer']):
                target_role = first_line

        if not company_name:
            comp_colon_match = re.search(r'(?:company|organization|employer|client)\s*:\s*([^\n\r]+)', job_desc, re.I)
            if comp_colon_match:
                target_company = comp_colon_match.group(1).strip()
            else:
                comp_match = re.search(r'(?:at|company|about)\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s+is|\s+we|\.|\n)', job_desc)
                if comp_match and len(comp_match.group(1).strip()) < 35:
                    target_company = comp_match.group(1).strip()

    return {
        "company": target_company,
        "role": target_role,
        "recipient": rec_name
    }


def generate_deterministic_outreach(
    resume_text: str,
    job_desc: str,
    mode: str = "cover_letter",
    tone: str = "confident",
    recipient_name: Optional[str] = None,
    company_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates high-fidelity outreach copy using deterministic templates and extracted metrics.
    """
    identity = _extract_candidate_identity(resume_text)
    context = _extract_target_context(job_desc, company_name, recipient_name)
    bullets = _extract_key_accomplishments(resume_text)

    cand_name = identity["name"]
    comp = context["company"]
    role = context["role"]
    recipient = context["recipient"]
    bullet1 = bullets[0] if len(bullets) > 0 else "Scaled high-throughput production infrastructure."
    bullet2 = bullets[1] if len(bullets) > 1 else "Optimized backend system latency and reliability."

    # Tone modifiers
    tone_adj = {
        "confident": "excited to bring a track record of high-impact engineering",
        "direct": "reaching out directly regarding my immediate technical fit for",
        "technical": "eager to leverage deep distributed systems and architecture experience for",
        "executive": "prepared to drive strategic engineering velocity and ROI for"
    }.get(tone.lower(), "pleased to present my qualifications for")

    if mode == "cover_letter":
        subject = f"Application for {role} - {cand_name}"
        body = f"""Dear {recipient},

I am {tone_adj} the {role} role at {comp}. With extensive hands-on experience solving complex technical challenges and optimizing production scale, I have consistently driven measurable outcomes across modern tech stacks.

Throughout my recent work, I have focused on solving high-friction operational bottlenecks:
• {bullet1}
• {bullet2}

What specifically excites me about {comp} is your engineering culture and commitment to solving mission-critical problems. I thrive in high-ownership environments where clean architecture and rapid execution intersect.

I would welcome the opportunity to discuss how my technical background and problem-solving framework directly align with {comp}'s upcoming milestones. Thank you for your time and consideration.

Sincerely,
{cand_name}
{identity.get('email', '')}"""

    elif mode == "linkedin_inmail":
        subject = f"{role} inquiry / Quick connection"
        body = f"""Hi {recipient},

Noticed your team at {comp} is scaling for the {role} position. Given my background ({bullet1.lower()}), I wanted to reach out directly.

I've recently focused on:
• {bullet1}
• {bullet2}

Would you be open to a brief 10-minute chat this week to see if my engineering background aligns with {comp}'s current priorities?

Best regards,
{cand_name}"""

    elif mode == "cold_email":
        subject = f"Ideas on scaling {role} at {comp} — {cand_name}"
        body = f"""Hi {recipient},

I know you're busy building at {comp}, so I'll keep this brief.

I saw that you're looking for a {role}. In my recent work, I delivered:
1. {bullet1}
2. {bullet2}

I've been following {comp}'s recent trajectory and would love to contribute the same high-velocity engineering rigor to your team.

Attached is my resume for reference. If this resonates, would you have 10 minutes for a brief conversation this Tuesday or Thursday?

Thanks,
{cand_name}
{identity.get('email', '')}"""

    elif mode == "follow_up":
        subject = f"Following up on {role} application — {cand_name}"
        body = f"""Hi {recipient},

I wanted to quickly follow up regarding my application for the {role} position at {comp}. 

I remain very enthusiastic about the opportunity to contribute to {comp}'s engineering initiatives, particularly in scaling systems and delivering high-impact technical solutions.

Please let me know if you need any additional portfolio samples, references, or context from my end.

Best regards,
{cand_name}"""

    else:
        subject = f"{role} Application"
        body = f"Hello {recipient},\n\nInterested in the {role} position at {comp}.\n\nBest,\n{cand_name}"

    word_count = len(body.split())
    reading_time_sec = max(10, round((word_count / 220) * 60))

    return {
        "mode": mode,
        "tone": tone,
        "subject": subject,
        "body": body.strip(),
        "word_count": word_count,
        "estimated_reading_time_seconds": reading_time_sec,
        "ai_powered": False,
        "target_context": {
            "candidate_name": cand_name,
            "company": comp,
            "role": role,
            "recipient": recipient
        }
    }


async def generate_outreach(
    resume_text: str,
    job_description: Optional[str] = None,
    mode: str = "cover_letter",
    tone: str = "confident",
    recipient_name: Optional[str] = None,
    company_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main generator coordinator using Google Gemini AI if configured,
    or falling back gracefully to deterministic synthesis.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key or gemini_api_key.startswith("your_") or len(gemini_api_key) < 15:
        return generate_deterministic_outreach(
            resume_text=resume_text,
            job_desc=job_description or "",
            mode=mode,
            tone=tone,
            recipient_name=recipient_name,
            company_name=company_name
        )

    try:
        from google import genai
        client = genai.Client(api_key=gemini_api_key)

        mode_instructions = {
            "cover_letter": "Write a 200-240 word modern, high-impact Cover Letter using the Google XYZ accomplishment framework. Highlight the candidate's top 2 matching metrics.",
            "linkedin_inmail": "Write an 80-110 word high-conversion LinkedIn Recruiter InMail / DM. Keep it punchy: Attention Hook -> Core Metric Bullet -> Low-friction 10-min chat CTA.",
            "cold_email": "Write a 120-150 word Hiring Manager Cold Email with a high open-rate Subject line and 3 crisp paragraphs.",
            "follow_up": "Write a 50-70 word polite, professional Follow-Up note maintaining momentum."
        }.get(mode, "Write a professional outreach message.")

        prompt = f"""You are an elite career strategist and executive copywriter.
Generate personalized outreach copy based on the candidate's resume and target job requirements.

TASK: {mode_instructions}
TONE: {tone} (Style: {'Assertive and energetic' if tone == 'confident' else 'Metric-focused and concise' if tone == 'direct' else 'Deep technical depth' if tone == 'technical' else 'Strategic leadership and ROI'})
RECIPIENT: {recipient_name or 'Hiring Team'}
COMPANY: {company_name or 'Target Company'}

CANDIDATE RESUME:
{resume_text[:2500]}

TARGET JOB DESCRIPTION:
{job_description[:2000] if job_description else "Tech Role at high-growth organization"}

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this exact schema:
{{
  "subject": "Email or InMail subject line",
  "body": "The full outreach message body text with proper line breaks"
}}
"""

        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        resp_text = response.text.strip()
        if "```json" in resp_text:
            resp_text = resp_text.split("```json")[1].split("```")[0].strip()
        elif "```" in resp_text:
            resp_text = resp_text.split("```")[1].split("```")[0].strip()

        parsed = json.loads(resp_text)
        subject = parsed.get("subject", "Application")
        body = parsed.get("body", "").strip()

        word_count = len(body.split())
        reading_time_sec = max(10, round((word_count / 220) * 60))

        context = _extract_target_context(job_description or "", company_name, recipient_name)
        identity = _extract_candidate_identity(resume_text)

        return {
            "mode": mode,
            "tone": tone,
            "subject": subject,
            "body": body,
            "word_count": word_count,
            "estimated_reading_time_seconds": reading_time_sec,
            "ai_powered": True,
            "target_context": {
                "candidate_name": identity["name"],
                "company": context["company"],
                "role": context["role"],
                "recipient": context["recipient"]
            }
        }

    except Exception as err:
        logger.warning(f"Gemini outreach generation failed: {err}. Falling back to deterministic engine.")
        return generate_deterministic_outreach(
            resume_text=resume_text,
            job_desc=job_description or "",
            mode=mode,
            tone=tone,
            recipient_name=recipient_name,
            company_name=company_name
        )
