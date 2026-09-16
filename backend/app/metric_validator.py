"""
Vanity Metric vs Business Outcome Disambiguation Engine Module
Calibrates Google/IBM X-Y-Z quantifiable metrics to distinguish true business outcomes
(revenue, latency reduction, throughput, cost savings, uptime SLAs) from vanity activity counts
("attended 50 meetings", "wrote 1,000 lines of code") and technical version false-positives
("Python 3.11", "Port 8080").
Applies the canonical Google/IBM -20 pt vanity deduction for unanchored activity numbers.
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("MetricValidator")

# High-impact business outcome regex patterns
BUSINESS_OUTCOME_PATTERNS = [
    # Currency / Financial Impact ($10M, $500K, €50k, £1.2M, etc.)
    (r'[\$\€\£\¥]\s*\d+(?:\.\d+)?\s*(?:k|m|b|billion|million|thousand)?\b', "financial_impact"),
    # Percentages of change / growth / reduction (+35%, 50% decrease, 99.99% uptime)
    (r'(?:[+\-]?\s*\d+(?:\.\d+)?\s*%\s*(?:increase|decrease|reduction|growth|improvement|reduction|boost|uptime|availability|retention)?)', "percentage_impact"),
    # Latency / Execution Time (under 1.5s, 120ms, 45 seconds, 2x faster)
    (r'\b\d+(?:\.\d+)?\s*(?:ms|milliseconds?|seconds?|mins?|minutes?|hours?)\b', "latency_time_reduction"),
    (r'\b\d+(?:\.\d+)?\s*x\s*(?:faster|speedup|throughput|improvement|reduction)\b', "multiplier_speedup"),
    # Scale & High Throughput (10M MAU, 50,000 RPS, 500TB data, 100K users)
    (r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:k|m|b|million|billion|thousand)?\s*(?:users?|customers?|clients?|dau|mau|requests?|qps|rps|tps|transactions?|gb|tb|pb)\b', "scale_throughput"),
    # Reliability / Availability SLAs (99.9%, 99.99%, five nines)
    (r'\b(?:99\.\d{1,4}%|five\s+nines|zero\s+downtime)\b', "high_availability_sla"),
]

# Vanity activity regex patterns (activity counts without value)
VANITY_ACTIVITY_PATTERNS = [
    (r'\b(?:attended|participated\s+in)\s+\d+\s+(?:meetings?|sessions?|standups?|calls?)\b', "meeting_attendance"),
    (r'\b(?:wrote|coded|authored|generated)\s+\d+(?:,\d{3})*\s+(?:lines\s+of\s+code|loc)\b', "loc_vanity"),
    (r'\b(?:closed|resolved|handled|fixed)\s+\d+\s+(?:tickets?|jira\s+tickets?|bugs?|issues?)\b', "ticket_churn"),
    (r'\b(?:read|reviewed)\s+\d+\s+(?:books?|articles?|whitepapers?)\b', "reading_count"),
    (r'\b(?:sent|drafted)\s+\d+\s+(?:emails?|messages?|slack\s+messages?)\b', "messaging_churn"),
]

# False positive indicators (versions, ports, protocols, RFCs)
FALSE_POSITIVE_PATTERNS = [
    r'\b(?:python|java|node(?:\.js)?|react|angular|vue|php|ruby|go|rust|c\+\+|dotnet|\.net)\s+[vV]?\d+(?:\.\d+)+\b',
    r'\b(?:port\s+\d{2,5}|ports\s+\d{2,5}(?:\s*,\s*\d{2,5})*)\b',
    r'\b(?:rfc\s*\d{3,5}|iso\s*\d{4,5}|ieee\s*\d{3,4})\b',
    r'\b(?:http(?:s)?|oauth|tls|ssl|ipv4|ipv6|usb|pci)\s*[vV]?\d*(?:\.\d+)*\b',
    r'\b(?:win|windows|macos|ios|android)\s+\d+(?:\.\d+)?\b',
    r'\b\d{1,2}(?:st|nd|rd|th)\s+(?:century|edition|place)\b'
]


def audit_bullet_metrics(bullet: str) -> Dict[str, Any]:
    """
    Audits a bullet point statement for quantifiable metrics, disambiguating
    true business outcomes from vanity activity counts and technical version false-positives.

    :param bullet: Single resume bullet point statement
    :return: Metric audit report with classification, detected metrics, and penalty points
    """
    if not bullet or not bullet.strip():
        return {
            "has_metric": False,
            "metric_type": "none",
            "has_business_outcome": False,
            "has_vanity_metric": False,
            "vanity_penalty": 0,
            "detected_outcomes": [],
            "detected_vanity": [],
            "detected_false_positives": [],
            "verdict": "No Metric Present",
            "feedback": "Add quantifiable business outcomes (e.g. % efficiency gain, $ saved, latency reduction)."
        }

    detected_outcomes = []
    detected_vanity = []
    detected_false_positives = []

    # 1. Check for False Positives first
    for pattern in FALSE_POSITIVE_PATTERNS:
        matches = re.findall(pattern, bullet, re.IGNORECASE)
        for m in matches:
            detected_false_positives.append(m if isinstance(m, str) else str(m))

    # Mask false positives in text copy to prevent collision
    sanitized_bullet = bullet
    for fp in detected_false_positives:
        sanitized_bullet = sanitized_bullet.replace(fp, " [TECH_REF] ")

    # 2. Check for Vanity Activities
    for pattern, category in VANITY_ACTIVITY_PATTERNS:
        matches = re.findall(pattern, sanitized_bullet, re.IGNORECASE)
        for m in matches:
            detected_vanity.append({"match": m, "category": category})

    # 3. Check for Business Outcomes
    for pattern, category in BUSINESS_OUTCOME_PATTERNS:
        matches = re.findall(pattern, sanitized_bullet, re.IGNORECASE)
        for m in matches:
            match_str = m if isinstance(m, str) else m[0]
            if match_str and match_str.strip():
                detected_outcomes.append({"match": match_str.strip(), "category": category})

    has_business_outcome = len(detected_outcomes) > 0
    has_vanity_metric = len(detected_vanity) > 0
    vanity_penalty = 20 if (has_vanity_metric and not has_business_outcome) else (10 if has_vanity_metric else 0)

    if has_business_outcome and not has_vanity_metric:
        metric_type = "business_outcome"
        verdict = "Strong Business Outcome"
        feedback = "Excellent quantifiable business metric demonstrating tangible organizational impact."
    elif has_business_outcome and has_vanity_metric:
        metric_type = "mixed"
        verdict = "Mixed Outcome with Vanity Activity"
        feedback = "Contains solid impact metrics alongside unanchored activity counts. Remove vanity numbers."
    elif has_vanity_metric:
        metric_type = "vanity_activity"
        verdict = "Vanity Activity Detected"
        feedback = "Applies -20 pt penalty. Replace arbitrary task counts with business outcomes (revenue, latency, scale, % improvement)."
    elif detected_false_positives:
        metric_type = "false_positive"
        verdict = "Technical Version False-Positive"
        feedback = "Version numbers or network ports detected as numbers. These do not count as quantifiable achievements."
    else:
        metric_type = "none"
        verdict = "No Metric Present"
        feedback = "No measurable metric found. Quantify result with % improvement, dollar value, or throughput."

    return {
        "has_metric": has_business_outcome or has_vanity_metric,
        "metric_type": metric_type,
        "has_business_outcome": has_business_outcome,
        "has_vanity_metric": has_vanity_metric,
        "vanity_penalty": vanity_penalty,
        "detected_outcomes": [o["match"] for o in detected_outcomes],
        "detected_vanity": [v["match"] for v in detected_vanity],
        "detected_false_positives": detected_false_positives,
        "verdict": verdict,
        "feedback": feedback
    }
