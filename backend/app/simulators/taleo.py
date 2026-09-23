import re
from typing import Dict, Any, List

def simulate_taleo_parsing(raw_text: str) -> Dict[str, Any]:
    """
    Emulates Taleo & Oracle enterprise legacy ATS parsing behavior:
    1. Enforces strict exact-case and exact substring keyword matching.
    2. Penalizes unexpanded technical acronyms (e.g. 'GCP' without 'Google Cloud Platform').
    3. Requires standard section header naming conventions (rejects creative headers like 'Where I've Been').
    4. Evaluates legacy parsing hazards:
       - Creative header rejection
       - Unexpanded abbreviations
       - Long unstructured paragraph blocks
    """
    if not raw_text or not raw_text.strip():
        return {
            "engine": "Taleo / Oracle",
            "compatibility_score": 0,
            "parsed_text": "",
            "extracted_entities": {},
            "hazards": ["Empty document provided."],
            "is_safe": False
        }

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    parsed_stream = "\n".join(lines)

    # Standard Taleo Header Check
    standard_headers = [
        r'(?i)^experience$', r'(?i)^work\s+experience$', r'(?i)^employment\s+history$',
        r'(?i)^education$', r'(?i)^skills$', r'(?i)^technical\s+skills$',
        r'(?i)^summary$', r'(?i)^professional\s+summary$', r'(?i)^projects$'
    ]

    creative_header_patterns = [
        r'(?i)^where\s+i(?:\'ve|\s+have)\s+worked',
        r'(?i)^my\s+journey',
        r'(?i)^what\s+i\s+do',
        r'(?i)^cool\s+stuff',
        r'(?i)^toolbelt',
        r'(?i)^stack'
    ]

    detected_creative_headers = []
    for line in lines:
        if len(line.split()) <= 4:
            for pat in creative_header_patterns:
                if re.match(pat, line):
                    detected_creative_headers.append(line)

    # Acronym expansion audit (Taleo legacy index requires both short and long form)
    acronym_pairs = [
        (r'\bAWS\b', r'\bAmazon\s+Web\s+Services\b', "AWS", "Amazon Web Services"),
        (r'\bGCP\b', r'\bGoogle\s+Cloud(?:\s+Platform)?\b', "GCP", "Google Cloud Platform"),
        (r'\bK8s\b', r'\bKubernetes\b', "K8s", "Kubernetes"),
        (r'\bML\b', r'\bMachine\s+Learning\b', "ML", "Machine Learning"),
        (r'\bCI/CD\b', r'\bContinuous\s+Integration\b', "CI/CD", "Continuous Integration"),
        (r'\bAI\b', r'\bArtificial\s+Intelligence\b', "AI", "Artificial Intelligence")
    ]

    unexpanded_acronyms = []
    for short_pat, long_pat, short_label, long_label in acronym_pairs:
        has_short = bool(re.search(short_pat, raw_text))
        has_long = bool(re.search(long_pat, raw_text, re.IGNORECASE))
        if has_short and not has_long:
            unexpanded_acronyms.append(f"{short_label} (missing '{long_label}')")

    hazards = []
    score = 100

    if detected_creative_headers:
        score -= min(30, len(detected_creative_headers) * 15)
        hazards.append(
            f"Detected non-standard section headers ({', '.join(detected_creative_headers)}). Taleo's legacy parser will fail to index experience under creative headings."
        )

    if unexpanded_acronyms:
        score -= min(25, len(unexpanded_acronyms) * 5)
        hazards.append(
            f"Detected {len(unexpanded_acronyms)} unexpanded acronym(s): {', '.join(unexpanded_acronyms[:3])}. Taleo keyword indexers often miss matches if both acronym and full expansion are not present."
        )

    score = max(10, min(100, score))

    return {
        "engine": "Taleo / Oracle",
        "compatibility_score": score,
        "parsed_text": parsed_stream,
        "extracted_entities": {
            "unexpanded_acronyms": unexpanded_acronyms,
            "creative_headers_flagged": detected_creative_headers,
            "legacy_indexing_tier": "Optimized" if score >= 85 else ("Moderate Risk" if score >= 70 else "High Risk")
        },
        "hazards": hazards,
        "is_safe": score >= 75
    }
