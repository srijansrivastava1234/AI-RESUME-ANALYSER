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
    ],
    "Healthcare & Clinical": [
        "patient care", "triage", "iv therapy", "vital signs", "wound care",
        "phlebotomy", "bls", "acls", "epic", "cerner", "hipaa", "medication administration",
        "emr", "ehr", "infection control", "telemetry", "icu", "cpr", "catheterization"
    ],
    "Finance & Accounting": [
        "gaap", "ifrs", "taxation", "general ledger", "financial modeling",
        "internal audit", "quickbooks", "sap", "excel", "reconciliation",
        "sox", "cpa", "financial reporting", "budgeting", "variance analysis",
        "accounts payable", "accounts receivable", "payroll"
    ],
    "Sales & Marketing": [
        "seo", "sem", "google analytics", "hubspot", "salesforce", "crm",
        "lead generation", "b2b sales", "conversion rate", "pipeline management",
        "content marketing", "meta ads", "email marketing", "cold outreach",
        "negotiation", "prospecting", "roas"
    ],
    "Operations & Project Management": [
        "supply chain", "logistics", "procurement", "inventory management",
        "six sigma", "lean", "pmp", "agile", "scrum", "vendor management",
        "erp", "quality assurance", "process optimization", "budget management", "kanban"
    ],
    "Human Resources": [
        "recruiting", "talent acquisition", "onboarding", "employee relations",
        "performance management", "workday", "adp", "benefits administration",
        "labor laws", "hris", "workplace safety", "compliance"
    ],
    "Legal & Compliance": [
        "contract drafting", "litigation", "due diligence", "intellectual property",
        "regulatory filings", "risk management", "legal research", "corporate governance", "m&a"
    ],
    "Design & Creative": [
        "figma", "sketch", "adobe xd", "photoshop", "illustrator",
        "wireframing", "prototyping", "user research", "usability testing",
        "design systems", "ui design", "ux design"
    ]
}

# Standard english stopwords to avoid false positive dynamic keywords
GENERIC_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "have", "has", "had",
    "will", "would", "should", "could", "been", "their", "they", "our", "you", "your",
    "must", "able", "plus", "years", "role", "work", "team", "looking", "about",
    "requirements", "qualifications", "responsibilities", "experience", "candidate",
    "position", "opportunity", "company", "skills", "ability", "strong", "knowledge",
    "understanding", "hands-on", "proven", "excellent", "working", "environment",
    "preferred", "required", "including", "across", "within", "ideal", "join", "help"
}

def extract_dynamic_job_keywords(job_text: str, top_n: int = 15) -> List[str]:
    """
    Extracts high-signal domain keywords directly from any Job Description.
    Allows non-tech and niche job descriptions (e.g. Culinary, Aviation, Healthcare, Law)
    to establish relevant keyword benchmarks dynamically.
    """
    if not job_text or not job_text.strip():
        return []

    text_clean = re.sub(r'[^a-zA-Z0-9\s\-\/\.]', ' ', job_text.lower())
    tokens = [t.strip("-./") for t in text_clean.split() if len(t.strip("-./")) >= 3]
    filtered_tokens = [t for t in tokens if t not in GENERIC_STOPWORDS and not t.isdigit()]

    # Extract 2-word domain phrases
    phrases = []
    for i in range(len(filtered_tokens) - 1):
        p = f"{filtered_tokens[i]} {filtered_tokens[i+1]}"
        if len(p) >= 7 and not any(w in GENERIC_STOPWORDS for w in p.split()):
            phrases.append(p)

    from collections import Counter
    counts = Counter(filtered_tokens + phrases)
    
    # Return top domain keywords
    return [term for term, _ in counts.most_common(top_n)]

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
        
    # If static taxonomy yielded sparse or zero matches (e.g. non-tech or specialized role),
    # dynamically extract domain keywords from the job description.
    if len(job_skills) < 3:
        dynamic_terms = extract_dynamic_job_keywords(job_text, top_n=10)
        job_skills.update(dynamic_terms)
        resume_lower = resume_text.lower()
        for term in dynamic_terms:
            if re.search(r'(?:\b|(?<=[^a-zA-Z0-9]))' + re.escape(term) + r'(?:\b|(?=[^a-zA-Z0-9]))', resume_lower):
                resume_skills.add(term)

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

