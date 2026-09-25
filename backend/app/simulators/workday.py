import re
from typing import Dict, Any, List

def simulate_workday_parsing(raw_text: str) -> Dict[str, Any]:
    """
    Emulates Workday ATS text parsing behavior and extraction mechanics:
    1. Strips page headers, footers, and page numbers.
    2. Simulates strict top-to-bottom vertical line scan (multi-column text flattening).
    3. Extracts standard Workday profile entities (Contact, Experience, Education, Skills).
    4. Evaluates structural risk (Multi-column interleaving, lost contact headers, date misalignment).

    :param raw_text: Raw plain text extracted from candidate resume document.
    :return: Standardized dictionary containing engine metadata, compatibility score (0-100),
             parsed text stream, extracted profile entities, hazards list, and safety boolean.
    """
    if not raw_text or not raw_text.strip():
        return {
            "engine": "Workday",
            "compatibility_score": 0,
            "parsed_text": "",
            "extracted_entities": {},
            "hazards": ["Empty document provided."],
            "is_safe": False
        }

    lines = raw_text.splitlines()
    cleaned_lines = []
    header_footer_lost = []
    column_traps = 0

    # Header / Footer patterns often stripped by Workday
    hf_patterns = [
        r'^\s*page\s+\d+(?:\s+of\s+\d+)?\s*$',
        r'^\s*\d+\s*/\s*\d+\s*$',
        r'^\s*curriculum\s+vitae\s*$',
        r'^\s*confidential\s*$'
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for header/footer strip
        is_hf = False
        for pat in hf_patterns:
            if re.match(pat, stripped, re.IGNORECASE):
                header_footer_lost.append(stripped)
                is_hf = True
                break
        if is_hf:
            continue

        # Detect horizontal tab/multi-space gutter (indicating multi-column table/sidebar)
        if re.search(r'\s{4,}|\t', line) and len(stripped) > 20:
            column_traps += 1

        cleaned_lines.append(stripped)

    parsed_stream = "\n".join(cleaned_lines)

    # Entity Extraction Simulation
    # 1. Contact (look in top 15 lines)
    top_block = " ".join(cleaned_lines[:15])
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', top_block)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', top_block)
    linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9_-]+', top_block, re.IGNORECASE)

    # 2. Section Detection
    experience_found = bool(re.search(r'(?i)\b(?:work\s+)?experience\b|\bemployment\b', parsed_stream))
    education_found = bool(re.search(r'(?i)\beducation\b|\bacademics?\b', parsed_stream))
    skills_found = bool(re.search(r'(?i)\b(?:technical\s+)?skills\b|\bcore\s+competencies\b', parsed_stream))

    hazards = []
    score = 100

    if column_traps > 2:
        penalty = min(35, column_traps * 6)
        score -= penalty
        hazards.append(
            f"Detected {column_traps} lines with multi-column spacing. Workday will flatten these horizontally, causing job titles and side-column skills to interlace into garbled text."
        )

    if not email_match:
        score -= 25
        hazards.append("Workday failed to locate a valid email in the primary candidate header.")

    if not experience_found:
        score -= 20
        hazards.append("Standard 'Work Experience' section header not detected by Workday parser.")

    if header_footer_lost:
        hazards.append(f"Workday stripped {len(header_footer_lost)} recurring header/footer line(s).")

    score = max(10, min(100, score))

    return {
        "engine": "Workday",
        "compatibility_score": score,
        "parsed_text": parsed_stream,
        "extracted_entities": {
            "candidate_name": cleaned_lines[0] if cleaned_lines else "Unknown",
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "linkedin": linkedin_match.group(0) if linkedin_match else None,
            "experience_detected": experience_found,
            "education_detected": education_found,
            "skills_detected": skills_found
        },
        "hazards": hazards,
        "is_safe": score >= 75
    }
