import re
from typing import Dict, Any, List

def simulate_successfactors_parsing(raw_text: str) -> Dict[str, Any]:
    """
    Emulates SAP SuccessFactors ATS XML candidate profile schema parsing:
    1. Structured Profile Field Mapping (Personal Data, Work Experience, Education, Certifications).
    2. Section Header Delimiter Conformance: Verifies standard SuccessFactors-recognized headers.
    3. Multi-language / Encoding Hazard Detection: Identifies character corruption risk.
    4. Table & Nested Column Interleaving Risk Assessment.
    """
    if not raw_text or not raw_text.strip():
        return {
            "engine": "SAP SuccessFactors",
            "compatibility_score": 0,
            "parsed_text": "",
            "extracted_fields": {},
            "hazards": ["Empty document provided."],
            "is_safe": False
        }

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    cleaned_stream = "\n".join(lines)
    text_lower = raw_text.lower()

    # 1. SuccessFactors Canonical Section Recognition
    canonical_sections = {
        "personal_info": r'\b(contact|personal information|contact information)\b',
        "work_experience": r'\b(experience|work experience|employment history|professional experience)\b',
        "education": r'\b(education|academic background|degrees|qualifications)\b',
        "skills": r'\b(skills|technical skills|core competencies|competencies)\b',
        "certifications": r'\b(certifications|certificates|licenses|accreditations)\b'
    }

    detected_sections = {}
    for sec_name, pattern in canonical_sections.items():
        match = re.search(pattern, text_lower)
        detected_sections[sec_name] = bool(match)

    # 2. Extract Candidate Profile Fields
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text)
    
    # Degrees detection
    degrees_pattern = r'\b(bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech|doctorate|associate)\b'
    degrees_found = list(set(re.findall(degrees_pattern, text_lower)))

    # Dates and chronological tenure blocks
    date_blocks = re.findall(r'\b(19\d\d|20\d\d)\s*(?:-|–|to)\s*(19\d\d|20\d\d|present|current)\b', text_lower)

    extracted_fields = {
        "has_contact_data": bool(email_match and phone_match),
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "sections_mapped": [k for k, v in detected_sections.items() if v],
        "degrees_identified": degrees_found,
        "employment_periods_count": len(date_blocks)
    }

    # 3. Assess Parsing Hazards & SuccessFactors Scoring
    hazards = []
    score = 100

    # Non-canonical header penalty
    missing_critical = [s for s in ["work_experience", "education", "skills"] if not detected_sections.get(s)]
    if missing_critical:
        penalty = len(missing_critical) * 15
        score -= penalty
        hazards.append(f"Missing standard SuccessFactors section header(s): {', '.join(missing_critical)}. XML mapping will misallocate blocks.")

    # Table formatting penalty (SuccessFactors XML parser fails on nested table structures)
    table_pipe_count = len(re.findall(r'\|', raw_text))
    table_border_count = len(re.findall(r'(\+{3,}|-{4,}|\t{2,})', raw_text))
    if table_pipe_count >= 3 or table_border_count >= 2:
        score -= 20
        hazards.append("Complex tabular or multi-tab formatting detected. SuccessFactors XML ingestion risks field scrambling.")

    # Date parseability check
    if len(date_blocks) == 0 and detected_sections.get("work_experience"):
        score -= 15
        hazards.append("Non-standard or unparseable employment date ranges. Ensure YYYY - YYYY format is used.")

    # Encoding / Non-standard unicode glyph check
    unusual_glyphs = len(re.findall(r'[^\x00-\x7F\u2010-\u2015\u2022\u2018-\u201D]', raw_text))
    if unusual_glyphs > 5:
        score -= 10
        hazards.append(f"Detected {unusual_glyphs} non-standard or foreign character glyphs that may corrupt SuccessFactors ISO-8859/UTF-8 profile mapping.")

    score = max(10, min(100, score))

    return {
        "engine": "SAP SuccessFactors",
        "compatibility_score": score,
        "parsed_text": cleaned_stream,
        "extracted_fields": extracted_fields,
        "hazards": hazards,
        "is_safe": score >= 75
    }
