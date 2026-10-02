"""Prompt Injection & Zero-Width Steganography Security Auditor.

Audits incoming candidate resume plain text and extracted document layers for:
1. LLM Prompt Injections / Jailbreak payloads (e.g., system instructions override, ignore previous instructions, roleplay jailbreaks).
2. Zero-width Unicode steganography characters (e.g., ZWSP \u200B, ZWNJ \u200C, ZWJ \u200D, BOM \uFEFF).
3. Concealed HTML comments (<!-- ... -->) and hidden script markers.
4. Delimiter manipulation attacks ([SYSTEM], <|im_start|>, [INST]).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List


# Zero-width Unicode characters used for steganography / invisible payloads
ZERO_WIDTH_CHARS = {
    "\u200B": "ZERO_WIDTH_SPACE",
    "\u200C": "ZERO_WIDTH_NON_JOINER",
    "\u200D": "ZERO_WIDTH_JOINER",
    "\uFEFF": "ZERO_WIDTH_NO_BREAK_SPACE_BOM",
    "\u2060": "WORD_JOINER",
    "\u180E": "MONGOLIAN_VOWEL_SEPARATOR",
    "\u200E": "LEFT_TO_RIGHT_MARK",
    "\u200F": "RIGHT_TO_LEFT_MARK",
}

ZERO_WIDTH_PATTERN = re.compile(r"[\u200B-\u200F\uFEFF\u2060\u180E]")

# Common prompt injection patterns tailored for AI recruiter / resume screening attacks
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"\b(?:ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions)\b", re.IGNORECASE),
    re.compile(r"\b(?:disregard\s+(?:all\s+)?(?:previous|prior)\s+prompts?)\b", re.IGNORECASE),
    re.compile(r"\b(?:you\s+are\s+now\s+(?:an?\s+)?(?:evaluator|hiring\s+manager|ai\s+assistant))\b", re.IGNORECASE),
    re.compile(r"\b(?:give\s+(?:this\s+candidate|me)\s+(?:a\s+score\s+of\s+100|10/10|a\s+perfect\s+score|maximum\s+points))\b", re.IGNORECASE),
    re.compile(r"\b(?:system\s+prompt\s+override)\b", re.IGNORECASE),
    re.compile(r"\b(?:new\s+instruction\s*:|admin\s+override\s*:)\b", re.IGNORECASE),
    re.compile(r"(?:\[SYSTEM\]|\[INST\]|<\|im_start\|>|<\|system\|>|Human:|Assistant:)", re.IGNORECASE),
]

# Hidden HTML / Comment patterns
HTML_COMMENT_PATTERN = re.compile(r"<!--[\s\S]*?-->", re.IGNORECASE)


def audit_prompt_injection_safety(text: str) -> Dict[str, Any]:
    """Scans resume content for adversarial prompt injection payloads and invisible steganography.

    Args:
        text: Raw resume plain text.

    Returns:
        Dict containing:
            - is_safe: bool
            - threat_level: str ("CLEAN", "LOW", "MEDIUM", "CRITICAL")
            - prompt_injections_found: List[str]
            - zero_width_chars_count: int
            - zero_width_char_types: List[str]
            - html_comments_found: List[str]
            - sanitized_text_sample: str (first 300 chars sanitized)
            - security_score: float (0.0 to 100.0)
            - recommendations: List[str]
    """
    if not text or not text.strip():
        return {
            "is_safe": True,
            "threat_level": "CLEAN",
            "prompt_injections_found": [],
            "zero_width_chars_count": 0,
            "zero_width_char_types": [],
            "html_comments_found": [],
            "sanitized_text_sample": "",
            "security_score": 100.0,
            "recommendations": ["No text provided for security auditing."],
        }

    injections_detected: List[str] = []
    
    # 1. Check prompt injection regexes
    for pat in PROMPT_INJECTION_PATTERNS:
        matches = pat.findall(text)
        for m in matches:
            injections_detected.append(f"Suspicious LLM prompt manipulation token: '{m}'")

    # 2. Check zero-width characters
    zw_matches = ZERO_WIDTH_PATTERN.findall(text)
    zw_types = list(set(ZERO_WIDTH_CHARS.get(ch, "UNKNOWN_ZERO_WIDTH") for ch in zw_matches))
    zw_count = len(zw_matches)

    # 3. Check HTML comments
    html_comments = HTML_COMMENT_PATTERN.findall(text)

    # Calculate threat level and security score
    threat_points = 0
    if injections_detected:
        threat_points += len(injections_detected) * 40
    if zw_count > 0:
        threat_points += min(40, zw_count * 5)
    if html_comments:
        threat_points += len(html_comments) * 20

    security_score = max(0.0, min(100.0, round(100.0 - threat_points, 1)))

    if threat_points == 0:
        threat_level = "CLEAN"
        is_safe = True
    elif threat_points < 30:
        threat_level = "LOW"
        is_safe = True
    elif threat_points < 70:
        threat_level = "MEDIUM"
        is_safe = False
    else:
        threat_level = "CRITICAL"
        is_safe = False

    # Sanitized preview
    sanitized = ZERO_WIDTH_PATTERN.sub("", text)
    sanitized = HTML_COMMENT_PATTERN.sub("", sanitized)
    sanitized_sample = sanitized[:300].strip()

    recommendations: List[str] = []
    if injections_detected:
        recommendations.append(
            "Adversarial LLM instruction patterns detected: Remove jailbreak phrases (e.g. 'ignore previous instructions', system overrides) which trigger automated ATS disqualification."
        )
    if zw_count > 0:
        recommendations.append(
            f"Detected {zw_count} zero-width hidden Unicode characters: Clean document encoding with UTF-8 normalization to remove invisible steganographic bytes."
        )
    if html_comments:
        recommendations.append(
            "Detected hidden HTML comment blocks: Strip HTML formatting before exporting document to standard ATS formats."
        )
    if not recommendations:
        recommendations.append(
            "Document is clean of adversarial prompt injections, steganographic bytes, and hidden HTML payloads."
        )

    return {
        "is_safe": is_safe,
        "threat_level": threat_level,
        "prompt_injections_found": injections_detected,
        "zero_width_chars_count": zw_count,
        "zero_width_char_types": zw_types,
        "html_comments_found": html_comments,
        "sanitized_text_sample": sanitized_sample,
        "security_score": security_score,
        "recommendations": recommendations,
    }
