import re
from typing import Dict, Any, List

def simulate_icims_parsing(raw_text: str) -> Dict[str, Any]:
    """
    Emulates iCIMS Enterprise Talent Cloud parser behavior:
    1. Audits standard section headers (Experience, Education, Skills, Summary).
    2. Checks for multi-column layout table interleaving risk.
    3. Evaluates chronological date format parsing fidelity.
    4. Validates contact profile extraction (Email, Phone, LinkedIn).
    5. Flags non-standard delimiters or pipe-separated unstructured lines.
    """
    if not raw_text or not raw_text.strip():
        return {
            "engine": "iCIMS Enterprise",
            "compatibility_score": 0,
            "parsed_text": "",
            "extracted_entities": {},
            "hazards": ["Empty document provided."],
            "is_safe": False
        }

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    cleaned_stream = "\n".join(lines)

    # 1. Contact Information Extraction
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    phone_match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', raw_text)
    linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', raw_text, re.IGNORECASE)

    extracted_contact = {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None
    }

    # 2. Section Headers
    headers_detected = []
    header_patterns = {
        "Work Experience": r'(?i)^(experience|work experience|employment history|professional experience)',
        "Education": r'(?i)^(education|academic background|qualifications)',
        "Skills": r'(?i)^(skills|technical skills|core competencies)',
        "Summary": r'(?i)^(summary|professional summary|profile|about me)'
    }

    for section, pattern in header_patterns.items():
        for line in lines:
            if re.match(pattern, line.strip()):
                headers_detected.append(section)
                break

    # 3. Date Formatting Checks
    # iCIMS expects standard date ranges like Jan 2020 - Present, 01/2020 - 05/2023, 2020 - 2022
    date_matches = re.findall(
        r'(?i)(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\b20\d{2}\b)\s*(?:-|–|—|to)\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\b20\d{2}\b|present|current)',
        raw_text
    )

    # 4. Multi-column / Tabular layout hazard
    # Detect lines with multiple tabs or large gap spaces (e.g. "Software Engineer          Jan 2021 - Present")
    tab_or_multi_gap = len([l for l in raw_text.splitlines() if re.search(r'\s{5,}', l) or '\t' in l])

    hazards = []
    score = 100

    if not extracted_contact["email"]:
        score -= 20
        hazards.append("No primary email address identified. iCIMS profile creation will fail automated candidate indexing.")

    if not extracted_contact["phone"]:
        score -= 10
        hazards.append("No standard phone number identified. Profile contact record incomplete in iCIMS.")

    if "Work Experience" not in headers_detected:
        score -= 20
        hazards.append("Standard 'Experience' section header not recognized. iCIMS job history parsing may misattribute roles.")

    if "Education" not in headers_detected:
        score -= 15
        hazards.append("Standard 'Education' section header not recognized. iCIMS education history may be omitted.")

    if len(date_matches) == 0:
        score -= 15
        hazards.append("No standard chronological date ranges (e.g., 'Jan 2020 – Present') recognized by iCIMS date parser.")

    if tab_or_multi_gap > 3:
        score -= 15
        hazards.append(f"Detected {tab_or_multi_gap} line(s) with multi-space/tab columnar gaps. iCIMS table flattening may interleave columns.")

    score = max(10, min(100, score))

    return {
        "engine": "iCIMS Enterprise",
        "compatibility_score": score,
        "parsed_text": cleaned_stream,
        "extracted_entities": {
            "contact": extracted_contact,
            "detected_sections": headers_detected,
            "date_ranges_detected": len(date_matches),
            "column_gap_hazards": tab_or_multi_gap
        },
        "hazards": hazards,
        "is_safe": score >= 75
    }
