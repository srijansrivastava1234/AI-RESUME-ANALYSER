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

def extract_skills_by_category(text: str) -> Dict[str, List[str]]:
    """
    Scans input text against the technical skill taxonomy and categorizes detected skills.
    """
    text_lower = text.lower()
    results: Dict[str, List[str]] = {}
    
    for category, skills in SKILL_TAXONOMY.items():
        matched = []
        for skill in skills:
            # Word boundary regex matching to avoid substring false positives (e.g., 'go' in 'good')
            pattern = r'(?:\b|(?<=[^a-zA-Z0-9]))' + re.escape(skill) + r'(?:\b|(?=[^a-zA-Z0-9]))'
            if re.search(pattern, text_lower):
                matched.append(skill.title() if len(skill) > 3 else skill.upper())
        if matched:
            results[category] = sorted(list(set(matched)))
            
    return results

def calculate_keyword_match_score(resume_text: str, job_text: str) -> Dict[str, any]:
    """
    Computes keyword overlap and missing keyword analysis between resume and job description.
    """
    if not job_text or not job_text.strip():
        return {
            "match_percentage": 100,
            "matched_keywords": [],
            "missing_keywords": []
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
            "missing_keywords": []
        }
        
    matched = resume_skills.intersection(job_skills)
    missing = job_skills - resume_skills
    
    match_percentage = int((len(matched) / len(job_skills)) * 100)
    
    return {
        "match_percentage": match_percentage,
        "matched_keywords": sorted([s.title() for s in matched]),
        "missing_keywords": sorted([s.title() for s in missing])
    }
