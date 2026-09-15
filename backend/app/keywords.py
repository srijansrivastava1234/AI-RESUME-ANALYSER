import re
from typing import Dict, List, Set

SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
        "rust", "ruby", "php", "scala", "swift", "kotlin", "sql", "html", "css", "bash"
    ],
    "Frameworks & Libraries": [
        "react", "next.js", "vue", "angular", "fastapi", "flask", "django",
        "express", "node.js", "nodejs", "spring boot", "tailwind", "redux", "pytorch", "tensorflow"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ci/cd", "github actions", "jenkins", "ansible", "linux", "nginx"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite",
        "dynamodb", "elasticsearch", "cassandra", "firebase", "snowflake", "bigquery"
    ],
    "Architecture & Methodologies": [
        "microservices", "rest api", "restful", "graphql", "system design",
        "agile", "scrum", "tdd", "unit testing", "oop", "distributed systems"
    ]
}

from functools import lru_cache

# Precompiled skill patterns for sub-millisecond keyword matching
_COMPILED_SKILL_PATTERNS: Dict[str, re.Pattern] = {
    skill: re.compile(
        r'(?:\b|(?<=[^a-zA-Z0-9]))' + re.escape(skill) + r'(?:\b|(?=[^a-zA-Z0-9]))'
    )
    for skills in SKILL_TAXONOMY.values()
    for skill in skills
}

def extract_skills_by_category(text: str) -> Dict[str, List[str]]:
    """
    Scans input text against the technical skill taxonomy and categorizes detected skills
    using precompiled regexes for maximum throughput.
    """
    if not text:
        return {}
    text_lower = text.lower()
    results: Dict[str, List[str]] = {}
    
    for category, skills in SKILL_TAXONOMY.items():
        matched = []
        for skill in skills:
            pattern = _COMPILED_SKILL_PATTERNS.get(skill)
            if pattern and pattern.search(text_lower):
                matched.append(skill.title() if len(skill) > 3 else skill.upper())
        if matched:
            results[category] = sorted(list(set(matched)))
            
    return results

def calculate_keyword_match_score(resume_text: str, job_text: str, enable_synonyms: bool = True) -> Dict[str, any]:
    """
    Computes keyword overlap and missing keyword analysis between resume and job description.
    When enable_synonyms=True, resolves technical acronyms (e.g. K8s <-> Kubernetes, TS <-> TypeScript).
    """
    if not job_text or not job_text.strip():
        return {
            "match_percentage": 100,
            "matched_keywords": [],
            "missing_keywords": [],
            "synonym_matches": []
        }
    
    resume_skills: Set[str] = set()
    for skills in extract_skills_by_category(resume_text).values():
        resume_skills.update([s.lower() for s in skills])
        
    job_skills: Set[str] = set()
    for skills in extract_skills_by_category(job_text).values():
        job_skills.update([s.lower() for s in skills])
        
    if not job_skills:
        return {
            "match_percentage": 100,
            "matched_keywords": sorted([s.title() for s in resume_skills]),
            "missing_keywords": [],
            "synonym_matches": []
        }

    if enable_synonyms:
        from app.acronyms import calculate_synonym_aware_overlap
        synonym_result = calculate_synonym_aware_overlap(resume_skills, job_skills)
        matched_all = set(synonym_result["exact_matches"])
        for sm in synonym_result["synonym_matches"]:
            matched_all.add(sm["job_term"])

        return {
            "match_percentage": synonym_result["match_percentage"],
            "matched_keywords": sorted(list(matched_all)),
            "missing_keywords": synonym_result["missing_skills"],
            "synonym_matches": synonym_result["synonym_matches"]
        }

    matched = resume_skills.intersection(job_skills)
    missing = job_skills - resume_skills
    match_percentage = int((len(matched) / len(job_skills)) * 100)
    
    return {
        "match_percentage": match_percentage,
        "matched_keywords": sorted([s.title() for s in matched]),
        "missing_keywords": sorted([s.title() for s in missing]),
        "synonym_matches": []
    }

