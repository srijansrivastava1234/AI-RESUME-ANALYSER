"""
Regional English Dialect Consistency & Grammatical Voice Auditor.
Detects US vs. UK spelling anomalies, mixed dialect usage, passive voice density,
and provides deterministic normalization dictionaries and active voice recommendations.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

# Regional Dialect Word Pairs: (US Spelling, UK Spelling)
DIALECT_PAIRS: List[Tuple[str, str]] = [
    ("optimize", "optimise"),
    ("optimized", "optimised"),
    ("optimizing", "optimising"),
    ("optimization", "optimisation"),
    ("analyze", "analyse"),
    ("analyzed", "analysed"),
    ("analyzing", "analysing"),
    ("analysis", "analysis"),
    ("color", "colour"),
    ("colored", "coloured"),
    ("colors", "colours"),
    ("behavior", "behaviour"),
    ("center", "centre"),
    ("centers", "centres"),
    ("centered", "centred"),
    ("traveled", "travelled"),
    ("traveling", "travelling"),
    ("program", "programme"),
    ("programs", "programmes"),
    ("defense", "defence"),
    ("catalog", "catalogue"),
    ("catalogs", "catalogues"),
    ("cataloged", "catalogued"),
    ("enrollment", "enrolment"),
    ("organize", "organise"),
    ("organized", "organised"),
    ("organizing", "organising"),
    ("organization", "organisation"),
    ("prioritize", "prioritise"),
    ("prioritized", "prioritised"),
    ("prioritizing", "prioritising"),
    ("prioritization", "prioritisation"),
    ("summarize", "summarise"),
    ("summarized", "summarised"),
    ("summarizing", "summarising"),
    ("judgment", "judgement"),
    ("license", "licence"),
    ("labor", "labour"),
    ("neighbor", "neighbour"),
    ("customize", "customise"),
    ("customized", "customised"),
    ("customizing", "customising"),
    ("customization", "customisation"),
    ("synchronize", "synchronise"),
    ("synchronized", "synchronised"),
    ("synchronizing", "synchronising"),
    ("synchronization", "synchronisation"),
    ("utilize", "utilise"),
    ("utilized", "utilised"),
    ("utilizing", "utilising"),
    ("utilization", "utilisation"),
    ("modeled", "modelled"),
    ("modeling", "modelling"),
]

US_TO_UK: Dict[str, str] = {us: uk for us, uk in DIALECT_PAIRS if us != uk}
UK_TO_US: Dict[str, str] = {uk: us for us, uk in DIALECT_PAIRS if us != uk}

PASSIVE_VOICE_PATTERNS: List[re.Pattern] = [
    re.compile(r"\b(?:was|were|is|are|been|being|be)\s+([a-z]+(?:ed|en|t))\s+by\b", re.IGNORECASE),
    re.compile(r"\b(?:was|were|is|are|been|being)\s+(?:responsible\s+for|tasked\s+with|involved\s+in|assigned\s+to)\b", re.IGNORECASE),
    re.compile(r"\b(?:was|were|has\s+been|have\s+been|had\s+been)\s+(?:developed|implemented|created|managed|designed|led|built|written|executed)\b", re.IGNORECASE),
]

def audit_dialect_and_voice(text: str) -> Dict[str, Any]:
    """
    Audits resume text for English dialect consistency (US vs UK)
    and passive voice patterns.
    """
    if not text or not text.strip():
        return {
            "predominant_dialect": "neutral",
            "us_term_count": 0,
            "uk_term_count": 0,
            "consistency_score": 100,
            "is_mixed": False,
            "detected_us_terms": [],
            "detected_uk_terms": [],
            "normalization_to_us": {},
            "normalization_to_uk": {},
            "passive_voice_count": 0,
            "passive_voice_snippets": [],
            "recommendations": []
        }

    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    us_found: Dict[str, int] = {}
    uk_found: Dict[str, int] = {}

    for token in tokens:
        if token in US_TO_UK:
            us_found[token] = us_found.get(token, 0) + 1
        elif token in UK_TO_US:
            uk_found[token] = uk_found.get(token, 0) + 1

    total_us = sum(us_found.values())
    total_uk = sum(uk_found.values())
    total_dialect_tokens = total_us + total_uk

    if total_dialect_tokens == 0:
        predominant = "neutral"
        consistency_score = 100
        is_mixed = False
    elif total_us >= total_uk:
        predominant = "US"
        consistency_score = round((total_us / total_dialect_tokens) * 100) if total_dialect_tokens > 0 else 100
        is_mixed = total_uk > 0
    else:
        predominant = "UK"
        consistency_score = round((total_uk / total_dialect_tokens) * 100) if total_dialect_tokens > 0 else 100
        is_mixed = total_us > 0

    # Passive voice detection
    passive_snippets = []
    lines = text.split("\n")
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        for pattern in PASSIVE_VOICE_PATTERNS:
            match = pattern.search(cleaned_line)
            if match:
                snippet = cleaned_line[:120] + ("..." if len(cleaned_line) > 120 else "")
                if snippet not in passive_snippets:
                    passive_snippets.append(snippet)

    # Conversion mappings
    to_us_map = {uk: UK_TO_US[uk] for uk in uk_found}
    to_uk_map = {us: US_TO_UK[us] for us in us_found}

    recommendations = []
    if is_mixed:
        recommendations.append(
            f"Mixed dialect detected ({total_us} US vs. {total_uk} UK terms). Standardize to {predominant} English for ATS consistency."
        )
    if passive_snippets:
        recommendations.append(
            f"Detected {len(passive_snippets)} passive voice constructions. Convert to active action verbs (e.g., replace 'was developed by' with 'Engineered')."
        )
    if consistency_score == 100 and total_dialect_tokens > 0:
        recommendations.append(f"Consistent {predominant} English usage maintained across all evaluated vocabulary.")

    return {
        "predominant_dialect": predominant,
        "us_term_count": total_us,
        "uk_term_count": total_uk,
        "consistency_score": consistency_score,
        "is_mixed": is_mixed,
        "detected_us_terms": list(us_found.keys()),
        "detected_uk_terms": list(uk_found.keys()),
        "normalization_to_us": to_us_map,
        "normalization_to_uk": to_uk_map,
        "passive_voice_count": len(passive_snippets),
        "passive_voice_snippets": passive_snippets[:10],
        "recommendations": recommendations
    }
