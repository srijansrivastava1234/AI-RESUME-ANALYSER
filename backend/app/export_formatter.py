"""
ATS-Safe Resume Export Formatter.
Serializes structured resume objects into standardized, single-column Markdown
and ASCII plaintext optimized for 100% ATS parser ingestion without text scrambling.
"""

import re
from typing import Dict, Any, List, Optional

TYPOGRAPHIC_REPLACEMENTS = {
    "\u2018": "'",  # Left single quotation mark
    "\u2019": "'",  # Right single quotation mark
    "\u201c": '"',  # Left double quotation mark
    "\u201d": '"',  # Right double quotation mark
    "\u2014": " - ",  # Em dash
    "\u2013": " - ",  # En dash
    "\u2022": "*",    # Bullet symbol
    "\u00a0": " ",    # Non-breaking space
    "\ufb01": "fi",   # Ligature fi
    "\ufb02": "fl",   # Ligature fl
    "\ufb00": "ff",   # Ligature ff
    "\ufb03": "ffi",  # Ligature ffi
    "\ufb04": "ffl",  # Ligature ffl
}


def sanitize_text_for_export(text: str) -> str:
    """Sanitizes text by replacing non-standard Unicode typography with clean ASCII equivalents."""
    if not text:
        return ""
    result = text
    for unicode_char, ascii_replacement in TYPOGRAPHIC_REPLACEMENTS.items():
        result = result.replace(unicode_char, ascii_replacement)
    # Remove control characters except newline and tab
    result = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", result)
    return result.strip()


def format_ats_markdown(resume_data: Dict[str, Any]) -> str:
    """
    Formats structured resume data into clean, ATS-optimized single-column Markdown.
    """
    if not resume_data:
        return ""

    lines: List[str] = []

    # Header / Contact Info
    name = sanitize_text_for_export(resume_data.get("name", "Candidate"))
    title = sanitize_text_for_export(resume_data.get("title", ""))
    lines.append(f"# {name}")
    if title:
        lines.append(f"**{title}**")

    contact_parts: List[str] = []
    if resume_data.get("email"):
        contact_parts.append(sanitize_text_for_export(resume_data["email"]))
    if resume_data.get("phone"):
        contact_parts.append(sanitize_text_for_export(resume_data["phone"]))
    if resume_data.get("location"):
        contact_parts.append(sanitize_text_for_export(resume_data["location"]))
    if resume_data.get("linkedin"):
        contact_parts.append(sanitize_text_for_export(resume_data["linkedin"]))
    if resume_data.get("github"):
        contact_parts.append(sanitize_text_for_export(resume_data["github"]))

    if contact_parts:
        lines.append(" | ".join(contact_parts))
    lines.append("")

    # Summary
    if resume_data.get("summary"):
        lines.append("## Professional Summary")
        lines.append(sanitize_text_for_export(resume_data["summary"]))
        lines.append("")

    # Skills
    if resume_data.get("skills"):
        lines.append("## Technical Skills")
        skills = resume_data["skills"]
        if isinstance(skills, list):
            lines.append(", ".join(sanitize_text_for_export(s) for s in skills))
        elif isinstance(skills, dict):
            for category, items in skills.items():
                cat_clean = sanitize_text_for_export(category)
                if isinstance(items, list):
                    items_clean = ", ".join(sanitize_text_for_export(i) for i in items)
                else:
                    items_clean = sanitize_text_for_export(str(items))
                lines.append(f"- **{cat_clean}:** {items_clean}")
        lines.append("")

    # Experience
    if resume_data.get("experience"):
        lines.append("## Work Experience")
        for exp in resume_data["experience"]:
            role = sanitize_text_for_export(exp.get("role", "Software Engineer"))
            company = sanitize_text_for_export(exp.get("company", "Company"))
            dates = sanitize_text_for_export(exp.get("dates", ""))
            location = sanitize_text_for_export(exp.get("location", ""))
            
            header_str = f"### {role} | {company}"
            if dates:
                header_str += f" | {dates}"
            if location:
                header_str += f" ({location})"
            lines.append(header_str)

            bullets = exp.get("bullets", [])
            for b in bullets:
                clean_b = sanitize_text_for_export(b)
                if clean_b:
                    lines.append(f"- {clean_b}")
            lines.append("")

    # Education
    if resume_data.get("education"):
        lines.append("## Education")
        for edu in resume_data["education"]:
            degree = sanitize_text_for_export(edu.get("degree", "B.S. in Computer Science"))
            institution = sanitize_text_for_export(edu.get("institution", "University"))
            year = sanitize_text_for_export(str(edu.get("year", "")))
            edu_str = f"- **{degree}**, {institution}"
            if year:
                edu_str += f" ({year})"
            lines.append(edu_str)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def format_ats_plaintext(resume_data: Dict[str, Any]) -> str:
    """
    Formats structured resume data into clean ASCII plaintext.
    """
    md = format_ats_markdown(resume_data)
    if not md:
        return ""
    # Strip markdown header syntax
    plain = re.sub(r"^#+\s*", "", md, flags=re.MULTILINE)
    # Strip bold markdown
    plain = re.sub(r"\*\*([^*]+)\*\*", r"\1", plain)
    return plain
