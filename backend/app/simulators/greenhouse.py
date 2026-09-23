import re
from typing import Dict, Any, List

def simulate_greenhouse_parsing(raw_text: str) -> Dict[str, Any]:
    """
    Emulates Greenhouse & Lever ATS text parsing behavior:
    1. Normalizes plain text into a structured semantic token stream.
    2. Clusters competencies into standard taxonomies (Frontend, Backend, Cloud, ML).
    3. Performs keyword proximity matching.
    4. Evaluates parsing confidence:
       - Recognizes bullet points and job achievement structure
       - Identifies non-standard glyphs or bullet artifacts
    """
    if not raw_text or not raw_text.strip():
        return {
            "engine": "Greenhouse / Lever",
            "compatibility_score": 0,
            "parsed_text": "",
            "extracted_entities": {},
            "hazards": ["Empty document provided."],
            "is_safe": False
        }

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    cleaned_stream = "\n".join(lines)

    # Detect bullet points
    bullet_lines = [l for l in lines if re.match(r'^[•\-–—*▪►✓]\s*', l) or re.match(r'^\d+\.\s', l)]
    bullet_count = len(bullet_lines)

    # Detect non-standard Unicode artifacts (e.g. icon glyphs, corrupted bullets)
    icon_artifacts = re.findall(r'[\uE000-\uF8FF\uFFFD\u200B-\u200D\uFEFF]', raw_text)
    
    # Skill clustering simulation
    text_lower = raw_text.lower()
    tech_clusters = {
        "Cloud & DevOps": ["aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd", "linux"],
        "Backend & APIs": ["python", "fastapi", "django", "node.js", "go", "java", "sql", "postgresql", "rest", "graphql"],
        "Frontend & UI": ["react", "typescript", "javascript", "vue", "angular", "html", "css", "tailwind"],
        "Data & AI": ["pandas", "numpy", "pytorch", "tensorflow", "spark", "scikit-learn", "sql", "machine learning"]
    }

    identified_clusters = {}
    total_found_skills = 0

    for cluster_name, skills in tech_clusters.items():
        found = [s for s in skills if re.search(r'(?<![a-zA-Z0-9_])' + re.escape(s) + r'(?![a-zA-Z0-9_])', text_lower)]
        if found:
            identified_clusters[cluster_name] = found
            total_found_skills += len(found)

    hazards = []
    score = 100

    if icon_artifacts:
        penalty = min(25, len(icon_artifacts) * 4)
        score -= penalty
        hazards.append(
            f"Detected {len(icon_artifacts)} unsupported Unicode icon glyph(s). Greenhouse tokenizers may replace these with corrupted characters."
        )

    if bullet_count < 3:
        score -= 20
        hazards.append("Few standard bullet points detected. Greenhouse parses achievements best when formatted with standard bullet prefixes (• or -).")

    if total_found_skills < 4:
        score -= 15
        hazards.append("Low technical skill cluster density. Ensure your skills are explicitly grouped in a dedicated Skills section.")

    score = max(10, min(100, score))

    return {
        "engine": "Greenhouse / Lever",
        "compatibility_score": score,
        "parsed_text": cleaned_stream,
        "extracted_entities": {
            "bullet_count": bullet_count,
            "skill_clusters": identified_clusters,
            "total_skills_detected": total_found_skills,
            "semantic_density": "High" if total_found_skills >= 8 else ("Medium" if total_found_skills >= 4 else "Low")
        },
        "hazards": hazards,
        "is_safe": score >= 75
    }
