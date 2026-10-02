"""Academic Credential Hierarchy & GPA Scale Normalizer.

Parses degree levels, honors distinctions, accreditation fields,
normalizes heterogeneous GPA scoring scales (4.0 scale, 10.0 CGPA scale,
and percentage metrics), and audits graduation timelines for ATS classification.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# Degree tier definitions and detection regexes
DEGREE_TIERS = {
    "DOCTORATE": {
        "tier_level": 5,
        "name": "Doctorate / Ph.D.",
        "regex": re.compile(r"\b(?:Ph\.?D\.?|Doctor of Philosophy|M\.?D\.?|J\.?D\.?|Doctorate)\b", re.IGNORECASE),
    },
    "MASTERS": {
        "tier_level": 4,
        "name": "Master's Degree",
        "regex": re.compile(
            r"\b(?:M\.?S\.?|M\.?Tech|M\.?Sc\.?|M\.?A\.?|M\.?Eng|MBA|Master of Science|Master of Technology|Master of Business Administration|Master of Arts|Master of Engineering|Master's)\b",
            re.IGNORECASE,
        ),
    },
    "BACHELORS": {
        "tier_level": 3,
        "name": "Bachelor's Degree",
        "regex": re.compile(
            r"\b(?:B\.?S\.?|B\.?Tech|B\.?Sc\.?|B\.?E\.?|B\.?A\.?|Bachelor of Science|Bachelor of Technology|Bachelor of Engineering|Bachelor of Arts|Bachelor's)\b",
            re.IGNORECASE,
        ),
    },
    "ASSOCIATES": {
        "tier_level": 2,
        "name": "Associate Degree",
        "regex": re.compile(r"\b(?:A\.?S\.?|A\.?A\.?|Associate of Science|Associate of Arts|Associate Degree)\b", re.IGNORECASE),
    },
    "BOOTCAMP_CERT": {
        "tier_level": 1,
        "name": "Bootcamp / Professional Certification",
        "regex": re.compile(r"\b(?:Bootcamp|Nanodegree|Certificate|Certification|Diploma|Coursera|edX)\b", re.IGNORECASE),
    },
}

# GPA Extraction regexes
GPA_4_SCALE_PATTERN = re.compile(
    r"\b(?:GPA|CGPA)\s*:?\s*(?P<val>[0-3]\.\d{1,3}|4\.00?)(?:\s*/\s*4(?:\.00?)?)?\b|\b(?P<val2>[0-3]\.\d{1,3}|4\.00?)\s*/\s*4(?:\.00?)?\b",
    re.IGNORECASE,
)
GPA_10_SCALE_PATTERN = re.compile(
    r"\b(?:CGPA|GPA)\s*:?\s*(?P<val>[5-9]\.\d{1,2}|10\.00?)(?:\s*/\s*10(?:\.00?)?)?\b|\b(?P<val2>[5-9]\.\d{1,2}|10\.00?)\s*/\s*10(?:\.00?)?\b",
    re.IGNORECASE,
)
PERCENTAGE_GRADE_PATTERN = re.compile(
    r"\b(?:Grade|Aggregate|Percentage|Marks)\s*:?\s*(?P<val>[5-9]\d(?:\.\d+)?|100)\s*%|\b(?P<val2>[5-9]\d(?:\.\d+)?|100)\s*%\b",
    re.IGNORECASE,
)

# Honors and Distinctions
HONORS_PATTERN = re.compile(
    r"\b(?:Summa\s+Cum\s+Laude|Magna\s+Cum\s+Laude|Cum\s+Laude|Dean'?s\s+List|First\s+Class\s+with\s+Distinction|First\s+Class|Honors|Valedictorian|Salutatorian)\b",
    re.IGNORECASE,
)

# Field of Study / Majors
MAJORS_PATTERN = re.compile(
    r"\b(?:Computer\s+Science|Software\s+Engineering|Electrical\s+Engineering|Data\s+Science|Information\s+Technology|Artificial\s+Intelligence|Machine\s+Learning|Cybersecurity|Mathematics|Physics|Mechanical\s+Engineering|Business\s+Administration|Finance|Economics)\b",
    re.IGNORECASE,
)

# Expected / Status patterns
IN_PROGRESS_PATTERN = re.compile(
    r"\b(?:Expected|Candidate|Expected\s+Graduation|Anticipated|In\s+Progress|Pursuing|202[5-9]|203\d)\b",
    re.IGNORECASE,
)


def parse_education_hierarchy(text: str) -> Dict[str, Any]:
    """Audits educational credentials, categorizes academic tiers, and normalizes GPA.

    Args:
        text: Raw resume plain text or education section.

    Returns:
        Dict containing:
            - highest_degree_tier: str
            - highest_degree_name: str
            - degree_tier_level: int (1 to 5)
            - detected_degrees: List[str]
            - majors_found: List[str]
            - honors_found: List[str]
            - normalized_gpa_4_scale: Optional[float]
            - raw_gpa_detected: Optional[str]
            - is_in_progress: bool
            - is_stem: bool
            - ats_education_score: float (0.0 to 100.0)
            - recommendations: List[str]
    """
    if not text or not text.strip():
        return {
            "highest_degree_tier": "NONE",
            "highest_degree_name": "No Degree Detected",
            "degree_tier_level": 0,
            "detected_degrees": [],
            "majors_found": [],
            "honors_found": [],
            "normalized_gpa_4_scale": None,
            "raw_gpa_detected": None,
            "is_in_progress": False,
            "is_stem": False,
            "ats_education_score": 0.0,
            "recommendations": ["No education section or academic credentials detected."],
        }

    detected_degrees: List[str] = []
    highest_tier_key = "NONE"
    highest_tier_name = "No Degree Detected"
    max_tier_level = 0

    for tier_key, tier_data in DEGREE_TIERS.items():
        matches = tier_data["regex"].findall(text)
        if matches:
            detected_degrees.extend(matches)
            if tier_data["tier_level"] > max_tier_level:
                max_tier_level = tier_data["tier_level"]
                highest_tier_key = tier_key
                highest_tier_name = tier_data["name"]

    # Detect Honors
    honors_found = list(set(HONORS_PATTERN.findall(text)))

    # Detect Majors
    majors_found = list(set(MAJORS_PATTERN.findall(text)))
    stem_majors = [
        "Computer Science",
        "Software Engineering",
        "Electrical Engineering",
        "Data Science",
        "Information Technology",
        "Artificial Intelligence",
        "Machine Learning",
        "Cybersecurity",
        "Mathematics",
        "Physics",
        "Mechanical Engineering",
    ]
    is_stem = any(m.title() in stem_majors or any(s.lower() in m.lower() for s in stem_majors) for m in majors_found)

    # Detect in-progress / expected graduation
    is_in_progress = bool(IN_PROGRESS_PATTERN.search(text))

    # Normalize GPA
    normalized_gpa: Optional[float] = None
    raw_gpa: Optional[str] = None

    # Check 4.0 scale
    m4 = GPA_4_SCALE_PATTERN.search(text)
    m10 = GPA_10_SCALE_PATTERN.search(text)
    mp = PERCENTAGE_GRADE_PATTERN.search(text)

    if m4:
        val_str = m4.group("val") or m4.group("val2")
        try:
            val = float(val_str)
            if val <= 4.0:
                normalized_gpa = round(val, 2)
                raw_gpa = f"{val}/4.0"
        except ValueError:
            pass
    elif m10:
        val_str = m10.group("val") or m10.group("val2")
        try:
            val = float(val_str)
            if val <= 10.0:
                # Convert 10.0 scale to 4.0 scale approx: (val / 10) * 4
                normalized_gpa = round((val / 10.0) * 4.0, 2)
                raw_gpa = f"{val}/10.0 CGPA"
        except ValueError:
            pass
    elif mp:
        val_str = mp.group("val") or mp.group("val2")
        try:
            val = float(val_str)
            normalized_gpa = round((val / 100.0) * 4.0, 2)
            raw_gpa = f"{val}%"
        except ValueError:
            pass

    # Calculate ATS Education Score
    # Tier level: 20 pts per tier up to 60 pts
    tier_pts = min(60.0, max_tier_level * 15.0)
    major_pts = 20.0 if majors_found else 0.0
    stem_pts = 10.0 if is_stem else 0.0
    honors_pts = 10.0 if honors_found else 0.0
    ats_score = min(100.0, tier_pts + major_pts + stem_pts + honors_pts)

    recommendations: List[str] = []
    if max_tier_level == 0:
        recommendations.append(
            "Explicitly list degree credentials (e.g. 'Bachelor of Science in Computer Science') with institution name."
        )
    if not majors_found:
        recommendations.append(
            "Clarify major / field of study (e.g., Computer Science, Electrical Engineering, Mathematics)."
        )
    if normalized_gpa and normalized_gpa < 3.0:
        recommendations.append(
            "Optional: If GPA is below 3.0/4.0, consider omitting numerical GPA and highlighting relevant coursework/projects instead."
        )
    if not recommendations:
        recommendations.append(
            "Education profile is robustly structured and formatted for enterprise ATS parsers."
        )

    return {
        "highest_degree_tier": highest_tier_key,
        "highest_degree_name": highest_tier_name,
        "degree_tier_level": max_tier_level,
        "detected_degrees": list(set(detected_degrees)),
        "majors_found": majors_found,
        "honors_found": honors_found,
        "normalized_gpa_4_scale": normalized_gpa,
        "raw_gpa_detected": raw_gpa,
        "is_in_progress": is_in_progress,
        "is_stem": is_stem,
        "ats_education_score": round(ats_score, 1),
        "recommendations": recommendations,
    }
