"""
Workday & Taleo Canonical Section Header Normalizer Module
Audits resume section headings against enterprise ATS canonical schemas (Workday,
Taleo, Ashby, Greenhouse, Lever). Non-canonical or creative headings (e.g., "Where I've
Been", "Things I've Built", "Toolbox") are dropped by automated field mappers, resulting
in missing experience or blank applicant profiles.
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("HeaderNormalizer")

# Canonical ATS section definitions and acceptable synonyms/aliases
CANONICAL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "Work Experience": {
        "mandatory": True,
        "weight": 35,
        "aliases": [
            r"work\s+experience",
            r"professional\s+experience",
            r"employment\s+history",
            r"work\s+history",
            r"relevant\s+experience",
            r"experience",
            r"career\s+history",
        ],
        "risky_creative": [
            r"where\s+i(?:'ve|\s+have)?\s+been",
            r"my\s+journey",
            r"career\s+journey",
            r"past\s+roles",
            r"what\s+i(?:'ve|\s+have)?\s+done",
        ]
    },
    "Education": {
        "mandatory": True,
        "weight": 25,
        "aliases": [
            r"education",
            r"academic\s+background",
            r"educational\s+background",
            r"academics",
            r"degrees",
            r"university\s+education",
            r"higher\s+education",
        ],
        "risky_creative": [
            r"alma\s+mater",
            r"where\s+i\s+studied",
            r"schooling",
            r"pedigree",
        ]
    },
    "Skills": {
        "mandatory": True,
        "weight": 25,
        "aliases": [
            r"skills",
            r"technical\s+skills",
            r"core\s+competencies",
            r"technologies",
            r"tech\s+stack",
            r"technical\s+proficiencies",
            r"skills\s*&\s*proficiencies",
            r"skills\s*&\s*abilities",
            r"tools\s*&\s*technologies",
        ],
        "risky_creative": [
            r"toolbox",
            r"my\s+toolkit",
            r"weapons\s+of\s+choice",
            r"what\s+i\s+know",
            r"brain\s+dump",
        ]
    },
    "Projects": {
        "mandatory": False,
        "weight": 10,
        "aliases": [
            r"projects",
            r"technical\s+projects",
            r"key\s+projects",
            r"selected\s+projects",
            r"personal\s+projects",
            r"open\s+source\s+contributions",
        ],
        "risky_creative": [
            r"things\s+i(?:'ve|\s+have)?\s+built",
            r"creations",
            r"hacks\s*&\s*builds",
            r"side\s+hustles",
        ]
    },
    "Certifications": {
        "mandatory": False,
        "weight": 5,
        "aliases": [
            r"certifications?",
            r"licenses?\s*(?:&|and)?\s*certifications?",
            r"credentials",
            r"professional\s+certifications?",
        ],
        "risky_creative": [
            r"badges",
            r"accreditations",
        ]
    },
    "Summary": {
        "mandatory": False,
        "weight": 0,
        "aliases": [
            r"summary",
            r"professional\s+summary",
            r"executive\s+summary",
            r"about\s+me",
            r"profile",
            r"career\s+overview",
        ],
        "risky_creative": [
            r"who\s+i\s+am",
            r"the\s+intro",
            r"elevator\s+pitch",
        ]
    }
}


def audit_section_headers(resume_text: str) -> Dict[str, Any]:
    """
    Scans a resume's text layer for section headings, classifying them into
    canonical Workday/Taleo headings, mapped synonyms, or non-canonical risky titles.

    :param resume_text: Extracted plain text of the resume
    :return: Audit report dictionary with canonical scores, mapped sections, and advice
    """
    if not resume_text or not resume_text.strip():
        return {
            "canonical_score": 0,
            "status": "Empty Text",
            "detected_sections": [],
            "missing_mandatory": ["Work Experience", "Education", "Skills"],
            "risky_creative_headers": [],
            "recommendations": ["Document contains no text to audit section headings."]
        }

    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    detected_sections: List[Dict[str, Any]] = []
    risky_creative_headers: List[Dict[str, str]] = []
    found_canonicals = set()

    for line in lines:
        # Check if line looks like a header (short length, optional markdown hashes or all-caps)
        cleaned_line = re.sub(r'^[#*\-_\s]+', '', line).strip()
        cleaned_line = re.sub(r'[:\s]+$', '', cleaned_line).strip()

        # Headers are usually <= 35 characters and <= 5 words
        if 2 <= len(cleaned_line) <= 40 and len(cleaned_line.split()) <= 5:
            matched_canonical = None

            # 1. Check direct aliases
            for canonical, data in CANONICAL_SCHEMAS.items():
                for alias in data["aliases"]:
                    if re.fullmatch(alias, cleaned_line, re.IGNORECASE):
                        matched_canonical = canonical
                        found_canonicals.add(canonical)
                        detected_sections.append({
                            "original_header": cleaned_line,
                            "canonical_name": canonical,
                            "is_canonical": True,
                            "risk_level": "Safe"
                        })
                        break
                if matched_canonical:
                    break

            # 2. Check risky creative variations if not matched
            if not matched_canonical:
                for canonical, data in CANONICAL_SCHEMAS.items():
                    for risky in data["risky_creative"]:
                        if re.search(risky, cleaned_line, re.IGNORECASE):
                            found_canonicals.add(canonical)
                            risky_item = {
                                "original_header": cleaned_line,
                                "recommended_canonical": canonical,
                                "risk_level": "High",
                                "reason": f"Enterprise ATS field mappers (Workday/Taleo) will fail to extract '{cleaned_line}'. Use '{canonical}' instead."
                            }
                            risky_creative_headers.append(risky_item)
                            detected_sections.append({
                                "original_header": cleaned_line,
                                "canonical_name": canonical,
                                "is_canonical": False,
                                "risk_level": "High"
                            })
                            matched_canonical = canonical
                            break
                    if matched_canonical:
                        break

    # Calculate missing mandatory sections
    missing_mandatory = []
    total_score = 100
    recommendations = []

    for canonical, data in CANONICAL_SCHEMAS.items():
        if data["mandatory"] and canonical not in found_canonicals:
            missing_mandatory.append(canonical)
            total_score -= data["weight"]
            recommendations.append(f"Missing mandatory section header '{canonical}'. Standard enterprise parsers require an explicit '{canonical}' heading.")

    # Deduct for risky creative headers
    if risky_creative_headers:
        total_score -= min(30, len(risky_creative_headers) * 15)
        for risky in risky_creative_headers:
            recommendations.append(
                f"Replace non-canonical header '{risky['original_header']}' with standard '{risky['recommended_canonical']}'."
            )

    canonical_score = max(0, min(100, total_score))

    if canonical_score >= 85:
        status = "ATS Compliant"
    elif canonical_score >= 60:
        status = "Partial Compliance"
    else:
        status = "High Risk of Parser Dropout"

    return {
        "canonical_score": canonical_score,
        "status": status,
        "detected_sections": detected_sections,
        "found_canonicals": list(found_canonicals),
        "missing_mandatory": missing_mandatory,
        "risky_creative_headers": risky_creative_headers,
        "recommendations": recommendations
    }
