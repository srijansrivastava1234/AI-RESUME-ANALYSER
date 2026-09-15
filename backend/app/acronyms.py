"""
Technical Acronym & Domain Synonym Expansion Graph.

Grounded in the ATS Validator Architecture:
- Solves candidate knockout where Job Descriptions use full names (e.g. "Kubernetes")
  and resumes use acronyms (e.g. "K8s"), or vice versa.
- Provides bidirectional canonical normalization across modern software engineering stacks:
  Languages, Cloud/DevOps, Databases, AI/ML, and Architectural Patterns.
"""

import re
from typing import Dict, List, Set, Tuple, Any

# Canonical clusters: canonical_name -> set of normalized alias strings (all lowercase)
TECH_SYNONYM_CLUSTERS: Dict[str, Set[str]] = {
    "Kubernetes": {"kubernetes", "k8s"},
    "Amazon Web Services": {"amazon web services", "aws"},
    "Google Cloud Platform": {"google cloud platform", "google cloud", "gcp"},
    "TypeScript": {"typescript", "ts"},
    "JavaScript": {"javascript", "js"},
    "PostgreSQL": {"postgresql", "postgres", "psql"},
    "Machine Learning": {"machine learning", "ml"},
    "Artificial Intelligence": {"artificial intelligence", "ai"},
    "Deep Learning": {"deep learning", "dl"},
    "Natural Language Processing": {"natural language processing", "nlp"},
    "Computer Vision": {"computer vision", "cv"},
    "Continuous Integration / Continuous Deployment": {"continuous integration", "continuous deployment", "ci/cd", "ci-cd", "cicd"},
    "TensorFlow": {"tensorflow", "tf"},
    "PyTorch": {"pytorch", "torch"},
    "Node.js": {"node.js", "nodejs", "node"},
    "React": {"react", "react.js", "reactjs"},
    "Vue": {"vue", "vue.js", "vuejs"},
    "Next.js": {"next.js", "nextjs", "next"},
    "MongoDB": {"mongodb", "mongo"},
    "Apache Kafka": {"apache kafka", "kafka"},
    "Apache Spark": {"apache spark", "spark"},
    "Docker": {"docker", "containerization", "containers"},
    "REST API": {"rest api", "restful", "restful api", "rest apis"},
    "GraphQL": {"graphql", "gql"},
    "Object-Oriented Programming": {"object-oriented programming", "oop"},
    "Test-Driven Development": {"test-driven development", "tdd"},
}

# Reverse index: alias -> canonical_name
_REVERSE_SYNONYM_MAP: Dict[str, str] = {}
for canonical, aliases in TECH_SYNONYM_CLUSTERS.items():
    _REVERSE_SYNONYM_MAP[canonical.lower()] = canonical
    for alias in aliases:
        _REVERSE_SYNONYM_MAP[alias.lower()] = canonical

# Precompiled boundary regexes for short acronyms to avoid false substring matches
# e.g., "\bml\b" should not match inside "html"
_SHORT_ACRONYMS = {"k8s", "aws", "gcp", "ts", "js", "ml", "ai", "dl", "nlp", "cv", "tf", "gql", "oop", "tdd"}
_COMPILED_SHORT_PATTERNS: Dict[str, re.Pattern] = {
    acronym: re.compile(r'(?:\b|(?<=[^a-zA-Z0-9]))' + re.escape(acronym) + r'(?:\b|(?=[^a-zA-Z0-9]))', re.IGNORECASE)
    for acronym in _SHORT_ACRONYMS
}


def get_canonical_term(term: str) -> str:
    """
    Returns the canonical standardized name for a given technical term or abbreviation.
    If no alias cluster exists, returns title-cased term.
    """
    if not term:
        return ""
    normalized = term.strip().lower()
    return _REVERSE_SYNONYM_MAP.get(normalized, term.strip().title())


def get_all_aliases(canonical_term: str) -> Set[str]:
    """
    Returns all aliases associated with a canonical technical term.
    """
    return TECH_SYNONYM_CLUSTERS.get(canonical_term, {canonical_term.lower()})


def expand_technical_terms(text: str) -> Dict[str, Any]:
    """
    Scans raw text and identifies technical abbreviations and their full expansions.
    
    :param text: Text string from resume or job description.
    :return: Dictionary containing detected acronyms, canonical mappings, and expansion details.
    """
    if not text:
        return {"detected_terms": [], "expansions": {}}

    text_lower = text.lower()
    detected_terms: Set[str] = set()
    expansions: Dict[str, str] = {}

    for canonical, aliases in TECH_SYNONYM_CLUSTERS.items():
        found = False
        for alias in aliases:
            if alias in _SHORT_ACRONYMS:
                pattern = _COMPILED_SHORT_PATTERNS.get(alias)
                if pattern and pattern.search(text):
                    found = True
                    detected_terms.add(alias.upper() if len(alias) <= 4 else alias.title())
            else:
                if alias in text_lower:
                    found = True
                    detected_terms.add(alias.title())

        if found:
            for alias in aliases:
                expansions[alias.title() if len(alias) > 3 else alias.upper()] = canonical

    return {
        "detected_terms": sorted(list(detected_terms)),
        "expansions": expansions
    }


def calculate_synonym_aware_overlap(
    resume_skills: Set[str],
    job_skills: Set[str]
) -> Dict[str, Any]:
    """
    Evaluates keyword overlap between resume and job description using
    the bidirectional technical synonym graph.
    
    Distinguishes:
    - Exact matches: term appeared identically in both
    - Synonym-resolved matches: term appeared under an alias/acronym (e.g. K8s vs Kubernetes)
    - True missing skills: not matched directly or via any synonym
    """
    if not job_skills:
        return {
            "match_percentage": 100,
            "exact_matches": sorted(list(resume_skills)),
            "synonym_matches": [],
            "missing_skills": []
        }

    # Normalize resume skills to canonical forms and track original
    resume_canonical_to_original: Dict[str, str] = {}
    for s in resume_skills:
        canonical = get_canonical_term(s)
        resume_canonical_to_original[canonical.lower()] = s

    exact_matches: List[str] = []
    synonym_matches: List[Dict[str, str]] = []
    missing_skills: List[str] = []

    for j_skill in job_skills:
        j_canonical = get_canonical_term(j_skill).lower()

        # 1. Exact match (case-insensitive)
        matched_exact = False
        for r_skill in resume_skills:
            if r_skill.lower() == j_skill.lower():
                exact_matches.append(j_skill.title() if len(j_skill) > 3 else j_skill.upper())
                matched_exact = True
                break

        if matched_exact:
            continue

        # 2. Synonym-resolved match
        if j_canonical in resume_canonical_to_original:
            resume_term = resume_canonical_to_original[j_canonical]
            canonical_name = get_canonical_term(j_skill)
            synonym_matches.append({
                "job_term": j_skill.title() if len(j_skill) > 3 else j_skill.upper(),
                "resume_term": resume_term.title() if len(resume_term) > 3 else resume_term.upper(),
                "canonical_term": canonical_name
            })
        else:
            missing_skills.append(j_skill.title() if len(j_skill) > 3 else j_skill.upper())

    total_job = len(job_skills)
    total_matched = len(exact_matches) + len(synonym_matches)
    match_percentage = int((total_matched / total_job) * 100) if total_job > 0 else 100

    return {
        "match_percentage": min(100, match_percentage),
        "exact_matches": sorted(exact_matches),
        "synonym_matches": sorted(synonym_matches, key=lambda x: x["job_term"]),
        "missing_skills": sorted(missing_skills)
    }
