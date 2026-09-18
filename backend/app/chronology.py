import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

CURRENT_YEAR = 2026
CURRENT_MONTH = 9

DATE_RANGE_REGEX = re.compile(
    r'(?P<start>(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?'
    r'\s+)?\d{4}(?:[-/.](?:0?[1-9]|1[0-2]))?)'
    r'\s*(?:[-–—]|to)\s*'
    r'(?P<end>(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?'
    r'\s+)?\d{4}(?:[-/.](?:0?[1-9]|1[0-2]))?|present|current|now)',
    re.IGNORECASE
)

NON_CANONICAL_PATTERNS = [
    (re.compile(r'\b(?:Spring|Summer|Fall|Winter|Autumn)\s+\d{4}\b', re.IGNORECASE), "Seasonal date notation (e.g., 'Spring 2022') is ambiguous to Workday and Taleo ATS engines. Use canonical 'Month YYYY' or 'YYYY-MM'."),
    (re.compile(r'\b\d+\s+(?:months?|years?)\s+ago\b', re.IGNORECASE), "Relative time expression detected (e.g., '2 years ago'). Enterprise parsers require absolute calendar dates."),
    (re.compile(r'\b(?:Q[1-4]|Quarter\s+[1-4])\s+\d{4}\b', re.IGNORECASE), "Quarterly date notation (e.g., 'Q3 2021') creates ambiguous employment duration in ATS filters.")
]

def _parse_date_token(token: str, default_to_current: bool = False) -> Tuple[int, int]:
    """
    Parses a single date string (e.g., 'Jan 2021', '2020-03', '2019', 'Present') into (year, month).
    """
    clean = token.strip().lower()
    if clean in ("present", "current", "now"):
        return CURRENT_YEAR, CURRENT_MONTH

    # Check for Month Name YYYY (e.g., "January 2020", "Jan 2020", "Jan. 2020")
    m_match = re.match(r'([a-z]+)\.?\s+(\d{4})', clean)
    if m_match:
        m_str, y_str = m_match.groups()
        month = MONTH_MAP.get(m_str[:3], 1)
        return int(y_str), month

    # Check for YYYY-MM or YYYY/MM
    ym_match = re.match(r'(\d{4})[-/.](0?[1-9]|1[0-2])', clean)
    if ym_match:
        y_str, m_str = ym_match.groups()
        return int(y_str), int(m_str)

    # Check for MM/YYYY
    my_match = re.match(r'(0?[1-9]|1[0-2])[-/.](\d{4})', clean)
    if my_match:
        m_str, y_str = my_match.groups()
        return int(y_str), int(m_str)

    # Check for YYYY alone
    y_match = re.match(r'(\d{4})', clean)
    if y_match:
        return int(y_match.group(1)), 1 if not default_to_current else 12

    return 2000, 1

def _months_between(start_y: int, start_m: int, end_y: int, end_m: int) -> int:
    return max(0, (end_y - start_y) * 12 + (end_m - start_m) + 1)

def _merge_intervals(intervals: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
    """
    Merges overlapping or contiguous career date intervals to prevent duplicate tenure counting.
    Input intervals: (start_y, start_m, end_y, end_m)
    """
    if not intervals:
        return []

    # Convert to continuous month offsets from year 1990
    def to_offset(y: int, m: int) -> int:
        return (y - 1990) * 12 + m

    def from_offset(off: int) -> Tuple[int, int]:
        return 1990 + (off // 12), (off % 12) or 12

    offset_intervals = []
    for sy, sm, ey, em in intervals:
        start_off = to_offset(sy, sm)
        end_off = to_offset(ey, em)
        if start_off <= end_off:
            offset_intervals.append((start_off, end_off))

    offset_intervals.sort(key=lambda x: x[0])
    merged: List[Tuple[int, int]] = []
    for start, end in offset_intervals:
        if not merged:
            merged.append((start, end))
        else:
            prev_start, prev_end = merged[-1]
            if start <= prev_end + 1:  # overlapping or directly consecutive
                merged[-1] = (prev_start, max(prev_end, end))
            else:
                merged.append((start, end))

    result = []
    for start_off, end_off in merged:
        sy, sm = from_offset(start_off)
        ey, em = from_offset(end_off)
        result.append((sy, sm, ey, em))
    return result

def audit_career_chronology(text: str) -> Dict[str, Any]:
    """
    Audits resume career timeline and date formatting:
    1. Extracts and normalizes career date ranges to ISO-compatible months.
    2. Merges overlapping tenures to compute accurate non-duplicative Years of Experience (YoE).
    3. Detects employment gaps (> 90 days / 3 months) and provides recruiter-safe talking hints.
    4. Identifies non-canonical seasonal or relative date patterns that trigger ATS parsing failures.
    5. Computes Chronology Parseability Score (0-100).
    """
    if not text or not text.strip():
        return {
            "chronology_score": 0,
            "timeline_health": "Empty Document",
            "total_experience_months": 0,
            "total_experience_years": 0.0,
            "detected_roles_count": 0,
            "career_gaps": [],
            "non_canonical_warnings": [],
            "date_ranges_detected": [],
            "recommendations": ["No resume text available to audit career chronology."]
        }

    # Detect non-canonical date warnings
    non_canonical_warnings: List[str] = []
    for pattern, warning in NON_CANONICAL_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            for m in set(matches):
                non_canonical_warnings.append(f"'{m}': {warning}")

    raw_ranges = []
    for match in DATE_RANGE_REGEX.finditer(text):
        start_raw = match.group("start")
        end_raw = match.group("end")
        sy, sm = _parse_date_token(start_raw, default_to_current=False)
        ey, em = _parse_date_token(end_raw, default_to_current=True)

        # Sanity bounds check (e.g. years between 1980 and current year + 1)
        if 1980 <= sy <= CURRENT_YEAR + 1 and 1980 <= ey <= CURRENT_YEAR + 1 and (ey > sy or (ey == sy and em >= sm)):
            raw_ranges.append({
                "raw_span": match.group(0),
                "start": f"{sy:04d}-{sm:02d}",
                "end": f"{ey:04d}-{em:02d}",
                "start_tuple": (sy, sm),
                "end_tuple": (ey, em),
                "duration_months": _months_between(sy, sm, ey, em)
            })

    if not raw_ranges:
        return {
            "chronology_score": 50,
            "timeline_health": "No Dates Detected",
            "total_experience_months": 0,
            "total_experience_years": 0.0,
            "detected_roles_count": 0,
            "career_gaps": [],
            "non_canonical_warnings": non_canonical_warnings,
            "date_ranges_detected": [],
            "recommendations": [
                "Could not detect standard calendar date ranges. Ensure employment dates follow "
                "standard 'Month YYYY - Month YYYY' or 'YYYY-MM - YYYY-MM' notation."
            ]
        }

    # Sort ranges by start date
    raw_ranges.sort(key=lambda r: (r["start_tuple"][0], r["start_tuple"][1]))

    # Merge intervals for accurate cumulative YoE
    interval_tuples = [(r["start_tuple"][0], r["start_tuple"][1], r["end_tuple"][0], r["end_tuple"][1]) for r in raw_ranges]
    merged_intervals = _merge_intervals(interval_tuples)

    total_months = 0
    for sy, sm, ey, em in merged_intervals:
        total_months += _months_between(sy, sm, ey, em)

    total_years = round(total_months / 12.0, 1)

    # Detect gaps between consecutive merged intervals
    career_gaps: List[Dict[str, Any]] = []
    for i in range(len(merged_intervals) - 1):
        prev_end = merged_intervals[i][2], merged_intervals[i][3]
        next_start = merged_intervals[i + 1][0], merged_intervals[i + 1][1]

        gap_months = (next_start[0] - prev_end[0]) * 12 + (next_start[1] - prev_end[1]) - 1
        if gap_months >= 3:  # Greater than 90 days
            career_gaps.append({
                "gap_start": f"{prev_end[0]:04d}-{prev_end[1]:02d}",
                "gap_end": f"{next_start[0]:04d}-{next_start[1]:02d}",
                "gap_duration_months": gap_months,
                "recruiter_advice": (
                    f"A {gap_months}-month gap detected between {prev_end[0]:04d}-{prev_end[1]:02d} and {next_start[0]:04d}-{next_start[1]:02d}. "
                    "Address this with brief context (e.g., sabbatical, contract consulting, specialized certs) to preempt ATS knockout."
                )
            })

    # Algorithmic scoring
    score = 100
    recommendations: List[str] = []

    # Non-canonical penalty
    if len(non_canonical_warnings) > 0:
        penalty = min(25, len(non_canonical_warnings) * 10)
        score -= penalty
        recommendations.append(
            f"Detected {len(non_canonical_warnings)} non-canonical date token(s). Enterprise ATS parsers (Workday, Taleo) "
            "often drop roles with seasonal or relative date formats from experience calculation."
        )

    # Career gap penalty (more than 1 large gap)
    long_gaps = [g for g in career_gaps if g["gap_duration_months"] > 6]
    if len(long_gaps) > 0:
        score -= min(20, len(long_gaps) * 10)
        recommendations.append(
            f"Detected {len(long_gaps)} employment gap(s) exceeding 6 months. Consider adding bridging projects, open-source work, or consulting."
        )

    score = max(0, min(100, score))

    if score >= 85:
        timeline_health = "Optimal Chronological Flow"
    elif score >= 65:
        timeline_health = "Minor Formatting Irregularities"
    else:
        timeline_health = "Chronological Parse Risk"

    if not recommendations:
        recommendations.append(
            f"Chronology verified: {total_years} years of experience detected across {len(raw_ranges)} role(s) with clean standard date formatting."
        )

    return {
        "chronology_score": score,
        "timeline_health": timeline_health,
        "total_experience_months": total_months,
        "total_experience_years": total_years,
        "detected_roles_count": len(raw_ranges),
        "date_ranges_detected": [
            {"span": r["raw_span"], "start": r["start"], "end": r["end"], "months": r["duration_months"]}
            for r in raw_ranges
        ],
        "career_gaps": career_gaps,
        "non_canonical_warnings": non_canonical_warnings,
        "recommendations": recommendations
    }
