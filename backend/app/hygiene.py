"""
ATS Formatting Hygiene & Section Completeness Evaluator.

Analyzes resume plain text to audit structural ATS compliance:
- Contact detail presence (Email, Phone, LinkedIn, GitHub)
- Essential section heading presence (Experience, Education, Skills, Projects)
- Length, character density, and structural hygiene flags
- Overall ATS formatting hygiene score (0 - 100)
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("ResumeHygiene")

# Regex patterns for contact information detection
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.IGNORECASE)
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LINKEDIN_REGEX = re.compile(r"(?:linkedin\.com/in/|linkedin\.com/pub/|linkedin:)\s*([a-zA-Z0-9_-]+)", re.IGNORECASE)
GITHUB_REGEX = re.compile(r"(?:github\.com/|github:)\s*([a-zA-Z0-9_-]+)", re.IGNORECASE)
PORTFOLIO_REGEX = re.compile(r"(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.(?:io|dev|me|tech|com)(?:/[^\s]*)?", re.IGNORECASE)

# Essential resume sections and typical header variants
STANDARD_SECTIONS = {
    "contact": ["contact", "email", "phone", "linkedin"],
    "experience": ["experience", "work history", "employment", "professional experience", "work experience"],
    "education": ["education", "academic", "university", "college", "degree", "bachelor", "master"],
    "skills": ["skills", "technical skills", "technologies", "competencies", "proficiencies", "core competencies"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "open source"],
    "certifications": ["certifications", "certificates", "credentials", "licenses", "accreditations"]
}


def audit_resume_hygiene(text: str) -> Dict[str, Any]:
    """
    Evaluates resume text for ATS formatting hygiene, section completeness,
    and contact info presence.

    :param text: Cleaned plain text of the resume
    :return: Dictionary containing hygiene score, checklist, contacts, and recommendations
    """
    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty for hygiene evaluation.")

    text_lower = text.lower()
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    # 1. Contact Information Auditing
    emails = EMAIL_REGEX.findall(text)
    phones = PHONE_REGEX.findall(text)
    linkedin_matches = LINKEDIN_REGEX.findall(text)
    github_matches = GITHUB_REGEX.findall(text)

    has_email = len(emails) > 0
    has_phone = len(phones) > 0
    has_linkedin = len(linkedin_matches) > 0
    has_github = len(github_matches) > 0

    contacts_detected = {
        "email": emails[0] if has_email else None,
        "phone": phones[0] if has_phone else None,
        "linkedin": linkedin_matches[0] if has_linkedin else None,
        "github": github_matches[0] if has_github else None,
    }

    # 2. Section Heading Auditing
    detected_sections = {}
    missing_sections = []

    for section_name, aliases in STANDARD_SECTIONS.items():
        found = any(re.search(rf"\b{re.escape(alias)}\b", text_lower) for alias in aliases)
        detected_sections[section_name] = found
        if not found and section_name != "certifications":
            missing_sections.append(section_name)

    # 3. Structural & Readability Signals
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    bullet_lines = [line for line in lines if line.startswith(("-", "•", "*", "–", "—")) or re.match(r"^\d+\.", line)]

    has_bullets = len(bullet_lines) >= 3
    is_word_count_optimal = 250 <= word_count <= 1200
    noise_characters = len(re.findall(r"[^\w\s.,;:()\-/@+]", text))
    noise_ratio = noise_characters / max(len(text), 1)
    is_low_noise = noise_ratio < 0.05

    # 4. Scoring Logic (Max 100)
    # Contact info: 25 points (Email 10, Phone 10, LinkedIn 5)
    contact_score = (10 if has_email else 0) + (10 if has_phone else 0) + (5 if has_linkedin else 0)

    # Sections: 45 points (Experience 15, Education 10, Skills 10, Projects 10)
    section_score = (
        (15 if detected_sections["experience"] else 0) +
        (10 if detected_sections["education"] else 0) +
        (10 if detected_sections["skills"] else 0) +
        (10 if detected_sections["projects"] else 0)
    )

    # Formatting & Structure: 30 points (Bullets 10, Length 10, Clean text 10)
    format_score = (
        (10 if has_bullets else 0) +
        (10 if is_word_count_optimal else 5) +
        (10 if is_low_noise else 0)
    )

    total_hygiene_score = contact_score + section_score + format_score

    # 5. Build Actionable Recommendations
    recommendations: List[str] = []
    if not has_email:
        recommendations.append("Add a professional email address at the top of your resume.")
    if not has_phone:
        recommendations.append("Include a contact phone number with country/area code.")
    if not has_linkedin:
        recommendations.append("Add your customized LinkedIn profile URL for recruiter verification.")
    if not detected_sections["experience"]:
        recommendations.append("Include a standard 'Experience' or 'Work History' section header.")
    if not detected_sections["skills"]:
        recommendations.append("Create a dedicated 'Skills' or 'Technical Proficiencies' section.")
    if not detected_sections["projects"]:
        recommendations.append("Showcase key technical projects under a 'Projects' section.")
    if not has_bullets:
        recommendations.append("Use bullet points for work experience to ensure ATS parsers segment achievements cleanly.")
    if word_count < 250:
        recommendations.append(f"Resume is short ({word_count} words). Aim for 350-800 words for balanced detail.")
    elif word_count > 1200:
        recommendations.append(f"Resume is lengthy ({word_count} words). Condense to 1-2 pages (~800 words max).")

    # 6. Build Checklist Items
    checklist = [
        {
            "name": "Email Address",
            "passed": has_email,
            "status": "PASS" if has_email else "FAIL",
            "detail": contacts_detected["email"] or "Missing email address"
        },
        {
            "name": "Phone Number",
            "passed": has_phone,
            "status": "PASS" if has_phone else "FAIL",
            "detail": contacts_detected["phone"] or "Missing phone number"
        },
        {
            "name": "LinkedIn Profile",
            "passed": has_linkedin,
            "status": "PASS" if has_linkedin else "WARNING",
            "detail": contacts_detected["linkedin"] or "No LinkedIn URL detected"
        },
        {
            "name": "GitHub Profile",
            "passed": has_github,
            "status": "PASS" if has_github else "INFO",
            "detail": contacts_detected["github"] or "Optional technical portfolio link"
        },
        {
            "name": "Work Experience Section",
            "passed": detected_sections["experience"],
            "status": "PASS" if detected_sections["experience"] else "FAIL",
            "detail": "Standard employment section detected" if detected_sections["experience"] else "Section header missing"
        },
        {
            "name": "Education Section",
            "passed": detected_sections["education"],
            "status": "PASS" if detected_sections["education"] else "FAIL",
            "detail": "Academic credentials section detected" if detected_sections["education"] else "Section header missing"
        },
        {
            "name": "Skills Section",
            "passed": detected_sections["skills"],
            "status": "PASS" if detected_sections["skills"] else "FAIL",
            "detail": "Categorized skill inventory detected" if detected_sections["skills"] else "Section header missing"
        },
        {
            "name": "Projects Section",
            "passed": detected_sections["projects"],
            "status": "PASS" if detected_sections["projects"] else "WARNING",
            "detail": "Project portfolio section detected" if detected_sections["projects"] else "Recommended for technical roles"
        },
        {
            "name": "Bullet Point Formatting",
            "passed": has_bullets,
            "status": "PASS" if has_bullets else "WARNING",
            "detail": f"{len(bullet_lines)} bullet items detected" if has_bullets else "Few or no bullet points detected"
        },
        {
            "name": "Document Length",
            "passed": is_word_count_optimal,
            "status": "PASS" if is_word_count_optimal else "WARNING",
            "detail": f"{word_count} words (optimal range: 250-1200 words)"
        }
    ]

    return {
        "hygiene_score": total_hygiene_score,
        "rating": "Excellent" if total_hygiene_score >= 85 else "Good" if total_hygiene_score >= 70 else "Needs Improvement",
        "word_count": word_count,
        "bullet_count": len(bullet_lines),
        "contacts": contacts_detected,
        "sections": detected_sections,
        "missing_sections": missing_sections,
        "checklist": checklist,
        "recommendations": recommendations,
    }
