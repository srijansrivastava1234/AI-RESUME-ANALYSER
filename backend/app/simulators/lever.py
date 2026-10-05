import re
from typing import Dict, Any, List

def simulate_lever_parsing(raw_text: str) -> Dict[str, Any]:
    """
    Emulates Lever ATS parsing & fast-tagging heuristics:
    1. Plain-text stream linearization & formatting strip.
    2. Automated Candidate Fast-Tag extraction (Role, Seniority, Tech Stack, Certifications).
    3. Contextual Skill Proximity Index: Computes whether skills appear within action contexts
       or as uncontextualized keyword dumps.
    4. Evaluates parsing confidence and structural hazards.
    """
    if not raw_text or not raw_text.strip():
        return {
            "engine": "Lever",
            "compatibility_score": 0,
            "parsed_text": "",
            "extracted_entities": {},
            "hazards": ["Empty document provided."],
            "is_safe": False
        }

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    cleaned_stream = "\n".join(lines)
    text_lower = raw_text.lower()

    # 1. Fast-Tag Extraction
    fast_tags: List[str] = []
    
    # Seniority tags
    seniority_patterns = {
        "Senior": r'\b(senior|sr\.?|lead|principal|staff|architect)\b',
        "Entry/Junior": r'\b(junior|jr\.?|associate|intern|entry[- ]level)\b',
        "Management": r'\b(manager|director|vp|head of|lead)\b'
    }
    for tag, pat in seniority_patterns.items():
        if re.search(pat, text_lower):
            fast_tags.append(tag)

    # Core Skill / Tech Tags
    tech_tags_map = {
        "Python": r'\bpython\b',
        "TypeScript/JavaScript": r'\b(typescript|javascript|node\.?js)\b',
        "React/Frontend": r'\b(react|vue|angular|frontend|next\.?js)\b',
        "Cloud/AWS/GCP": r'\b(aws|gcp|azure|cloud|kubernetes|docker)\b',
        "Backend/Data": r'\b(fastapi|django|postgres|sql|nosql|spark|redis)\b',
        "AI/ML": r'\b(machine learning|ai|llm|pytorch|tensorflow|nlp)\b'
    }
    for tag, pat in tech_tags_map.items():
        if re.search(pat, text_lower):
            fast_tags.append(tag)

    # 2. Skill Proximity / Contextual Verification
    # Check if technical skills appear near impact verbs or numbers
    words = raw_text.split()
    contextualized_skill_count = 0
    raw_skill_mentions = 0

    action_verb_patterns = r'\b(built|designed|developed|engineered|optimized|deployed|architected|implemented|led|scaled)\b'
    
    for i, word in enumerate(words):
        cleaned_word = re.sub(r'[^a-zA-Z0-9#+]', '', word.lower())
        if cleaned_word in ["python", "react", "aws", "docker", "fastapi", "sql", "kubernetes", "typescript", "java", "c++"]:
            raw_skill_mentions += 1
            # Check window of +/- 10 words for action verbs or numeric metrics
            window_start = max(0, i - 10)
            window_end = min(len(words), i + 11)
            window_text = " ".join(words[window_start:window_end]).lower()
            if re.search(action_verb_patterns, window_text) or re.search(r'\b\d+(\.\d+)?%?|\$\d+\b', window_text):
                contextualized_skill_count += 1

    proximity_ratio = (contextualized_skill_count / raw_skill_mentions) if raw_skill_mentions > 0 else 0.0

    # 3. Detect Layout & Parsing Hazards
    hazards = []
    score = 100

    # Lever strips rich formatting; table or multi-column artifacts cause severe line interleaving
    table_pipes = len(re.findall(r'\|', raw_text))
    if table_pipes > 6:
        score -= 20
        hazards.append(f"Detected {table_pipes} pipe table separators. Lever plain-text extraction flattens tables, scrambling columns.")

    # Isolated keyword dumping penalty
    if raw_skill_mentions >= 5 and proximity_ratio < 0.4:
        score -= 15
        hazards.append("Low skill contextualization: Skills appear clustered in raw lists rather than tied to measurable achievements.")

    # Email / Phone detect
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text))

    if not has_email:
        score -= 25
        hazards.append("Missing or unparseable email address. Lever candidate profile creation will fail.")
    if not has_phone:
        score -= 10
        hazards.append("Missing candidate contact phone number.")

    if len(fast_tags) < 2:
        score -= 15
        hazards.append("Insufficient candidate Fast-Tags identified. Ensure standard role titles and key technical proficiencies are clearly stated.")

    score = max(10, min(100, score))

    return {
        "engine": "Lever",
        "compatibility_score": score,
        "parsed_text": cleaned_stream,
        "extracted_entities": {
            "fast_tags": sorted(list(set(fast_tags))),
            "raw_skill_count": raw_skill_mentions,
            "contextualized_skills": contextualized_skill_count,
            "proximity_score": round(proximity_ratio * 100, 1),
            "has_contact_info": has_email and has_phone
        },
        "hazards": hazards,
        "is_safe": score >= 75
    }
