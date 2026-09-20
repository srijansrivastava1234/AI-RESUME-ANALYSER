"""
Hard vs Soft Skill Taxonomy Classifier & Buzzword Dilution Detector
Segregates verifiable technical competencies from subjective buzzwords,
measures skill inventory dilution, and verifies cross-section substantiation.
"""

import re
from typing import Dict, List, Any, Optional, Set, Tuple

# Comprehensive taxonomy of canonical hard technical proficiencies
HARD_SKILL_TAXONOMY: Dict[str, str] = {
    # Programming Languages
    "python": "Language", "javascript": "Language", "typescript": "Language",
    "java": "Language", "c++": "Language", "c#": "Language", "go": "Language",
    "golang": "Language", "rust": "Language", "ruby": "Language", "php": "Language",
    "swift": "Language", "kotlin": "Language", "scala": "Language", "sql": "Language",
    "bash": "Language", "shell": "Language", "r": "Language",
    
    # Frameworks & Libraries
    "react": "Framework", "react.js": "Framework", "next.js": "Framework",
    "vue": "Framework", "vue.js": "Framework", "angular": "Framework",
    "node.js": "Framework", "nodejs": "Framework", "express": "Framework",
    "fastapi": "Framework", "flask": "Framework", "django": "Framework",
    "spring": "Framework", "spring boot": "Framework", ".net": "Framework",
    "asp.net": "Framework", "laravel": "Framework", "rails": "Framework",
    
    # Cloud & DevOps
    "aws": "Cloud/DevOps", "amazon web services": "Cloud/DevOps",
    "azure": "Cloud/DevOps", "gcp": "Cloud/DevOps", "google cloud": "Cloud/DevOps",
    "docker": "Cloud/DevOps", "kubernetes": "Cloud/DevOps", "k8s": "Cloud/DevOps",
    "terraform": "Cloud/DevOps", "ansible": "Cloud/DevOps", "helm": "Cloud/DevOps",
    "jenkins": "Cloud/DevOps", "github actions": "Cloud/DevOps", "gitlab ci": "Cloud/DevOps",
    "ci/cd": "Cloud/DevOps", "prometheus": "Cloud/DevOps", "grafana": "Cloud/DevOps",
    "linux": "Cloud/DevOps", "nginx": "Cloud/DevOps", "kafka": "Cloud/DevOps",
    
    # Databases & Storage
    "postgresql": "Database", "postgres": "Database", "mysql": "Database",
    "mongodb": "Database", "redis": "Database", "elasticsearch": "Database",
    "opensearch": "Database", "cassandra": "Database", "dynamodb": "Database",
    "sqlite": "Database", "snowflake": "Database", "bigquery": "Database",
    
    # AI & Machine Learning
    "machine learning": "AI/ML", "deep learning": "AI/ML", "nlp": "AI/ML",
    "computer vision": "AI/ML", "pytorch": "AI/ML", "tensorflow": "AI/ML",
    "keras": "AI/ML", "scikit-learn": "AI/ML", "pandas": "AI/ML",
    "numpy": "AI/ML", "hugging face": "AI/ML", "langchain": "AI/ML",
    "llm": "AI/ML", "transformers": "AI/ML", "vector database": "AI/ML",
    
    # Architecture, Protocols & Tooling
    "rest": "Architecture", "restful api": "Architecture", "graphql": "Architecture",
    "grpc": "Architecture", "microservices": "Architecture", "system design": "Architecture",
    "oauth": "Security", "jwt": "Security", "git": "Tooling", "jira": "Tooling"
}

# Canonical subjective buzzwords often improperly listed as skills
SOFT_SKILL_BUZZWORDS: Dict[str, str] = {
    "team player": "Collaboration",
    "teamwork": "Collaboration",
    "communication": "Interpersonal",
    "communication skills": "Interpersonal",
    "strong communication": "Interpersonal",
    "problem solver": "Cognitive",
    "problem solving": "Cognitive",
    "critical thinking": "Cognitive",
    "creative thinking": "Cognitive",
    "fast learner": "Adaptability",
    "quick learner": "Adaptability",
    "adaptability": "Adaptability",
    "self-starter": "Work Ethic",
    "self motivated": "Work Ethic",
    "hard worker": "Work Ethic",
    "work ethic": "Work Ethic",
    "detail oriented": "Work Ethic",
    "detail-oriented": "Work Ethic",
    "time management": "Organizational",
    "multitasking": "Organizational",
    "leadership": "Management",
    "strategic thinking": "Management",
    "thought leadership": "Management",
    "results-driven": "Attitude",
    "passionate": "Attitude",
    "enthusiastic": "Attitude",
    "go-getter": "Attitude"
}


def classify_single_skill(skill: str) -> Dict[str, Any]:
    """
    Classify a single skill string as HARD, SOFT, or UNCLASSIFIED.
    """
    cleaned = skill.strip().lower()
    cleaned = re.sub(r"^[•\-\*]\s*", "", cleaned)

    if cleaned in HARD_SKILL_TAXONOMY:
        return {
            "skill": skill.strip(),
            "type": "HARD",
            "category": HARD_SKILL_TAXONOMY[cleaned],
            "is_buzzword": False
        }

    if cleaned in SOFT_SKILL_BUZZWORDS:
        return {
            "skill": skill.strip(),
            "type": "SOFT",
            "category": SOFT_SKILL_BUZZWORDS[cleaned],
            "is_buzzword": True
        }

    # Partial / phrase matching for hard vs soft patterns
    for hard_key, category in HARD_SKILL_TAXONOMY.items():
        if re.search(r"\b" + re.escape(hard_key) + r"\b", cleaned):
            return {
                "skill": skill.strip(),
                "type": "HARD",
                "category": category,
                "is_buzzword": False
            }

    for soft_key, category in SOFT_SKILL_BUZZWORDS.items():
        if re.search(r"\b" + re.escape(soft_key) + r"\b", cleaned):
            return {
                "skill": skill.strip(),
                "type": "SOFT",
                "category": category,
                "is_buzzword": True
            }

    return {
        "skill": skill.strip(),
        "type": "UNCLASSIFIED",
        "category": "Domain Specific",
        "is_buzzword": False
    }


def audit_skills(
    skills_list: List[str],
    experience_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Audit and classify a candidate's skill inventory.
    Optionally cross-references against experience text to detect unsubstantiated skills.
    """
    classified_skills: List[Dict[str, Any]] = []
    hard_skills: List[Dict[str, Any]] = []
    soft_skills: List[Dict[str, Any]] = []
    unclassified_skills: List[Dict[str, Any]] = []

    seen = set()
    for s in skills_list:
        if not s or not s.strip():
            continue
        cleaned = s.strip()
        if cleaned.lower() in seen:
            continue
        seen.add(cleaned.lower())

        cls = classify_single_skill(cleaned)
        classified_skills.append(cls)
        if cls["type"] == "HARD":
            hard_skills.append(cls)
        elif cls["type"] == "SOFT":
            soft_skills.append(cls)
        else:
            unclassified_skills.append(cls)

    total_count = len(classified_skills)
    hard_count = len(hard_skills)
    soft_count = len(soft_skills)

    # Compute Hard-to-Soft ratio: R_skill = N_hard / (N_hard + N_soft)
    denom = hard_count + soft_count
    if denom > 0:
        hard_ratio = round((hard_count / denom) * 100, 1)
        soft_ratio = round((soft_count / denom) * 100, 1)
    else:
        hard_ratio = 100.0 if total_count > 0 else 0.0
        soft_ratio = 0.0

    # Cross-reference with experience bullets
    substantiated_skills: List[str] = []
    unsubstantiated_skills: List[str] = []
    
    if experience_text and hard_skills:
        exp_lower = experience_text.lower()
        for hs in hard_skills:
            skill_name = hs["skill"].lower()
            pattern = r"\b" + re.escape(skill_name) + r"\b"
            if re.search(pattern, exp_lower):
                substantiated_skills.append(hs["skill"])
            else:
                unsubstantiated_skills.append(hs["skill"])
        substantiation_rate = round((len(substantiated_skills) / hard_count) * 100, 1)
    else:
        substantiation_rate = 100.0 if hard_count > 0 else 0.0

    # Score calculation
    # Baseline: 100
    # Penalty: soft_ratio > 30% -> penalty = (soft_ratio - 30) * 1.5
    # Penalty: unsubstantiated_skills -> penalty = (100 - substantiation_rate) * 0.3
    penalties = 0.0
    warnings: List[str] = []

    if soft_ratio > 30.0:
        soft_penalty = round((soft_ratio - 30.0) * 1.2, 1)
        penalties += soft_penalty
        warnings.append(
            f"Soft skill buzzword dilution: {soft_ratio}% of your skills inventory consists of subjective traits "
            f"({', '.join([s['skill'] for s in soft_skills[:4]])}). Modern ATS parsers expect hard, demonstrable proficiencies."
        )

    if unsubstantiated_skills:
        unsub_penalty = round((len(unsubstantiated_skills) / max(1, hard_count)) * 25.0, 1)
        penalties += unsub_penalty
        warnings.append(
            f"{len(unsubstantiated_skills)} hard skills ({', '.join(unsubstantiated_skills[:5])}) are listed in skills but never "
            f"substantiated in your Work Experience bullets. Recruiters and Ashby/Workday downrank unverified skills."
        )

    credibility_index = max(0.0, min(100.0, round(100.0 - penalties, 1)))

    if credibility_index >= 85:
        status = "EXCELLENT"
    elif credibility_index >= 65:
        status = "MODERATE"
    else:
        status = "DILUTED"

    return {
        "credibility_index": credibility_index,
        "status": status,
        "total_skills": total_count,
        "hard_skills_count": hard_count,
        "soft_skills_count": soft_count,
        "unclassified_count": len(unclassified_skills),
        "hard_ratio": hard_ratio,
        "soft_ratio": soft_ratio,
        "substantiation_rate": substantiation_rate,
        "substantiated_skills": substantiated_skills,
        "unsubstantiated_skills": unsubstantiated_skills,
        "hard_skills": hard_skills,
        "soft_skills": soft_skills,
        "unclassified_skills": unclassified_skills,
        "warnings": warnings
    }
