"""
ATS Hack & Spam Detector Module
Audits resumes and raw markup for deceptive parser exploitation techniques:
- White text on white background (#ffffff, opacity: 0)
- Microscopic typography (font-size: 0px, 0.1pt, 1px)
- Off-screen text positioning (left: -9999px, display: none, visibility: hidden)
- Invisible Unicode zero-width character stuffing
- Unpunctuated keyword stuffing blobs and repetitive skill spamming

Modern enterprise ATS parsers (Workday, Taleo, Ashby, Greenhouse) parse DOM styles
and PDF graphics state operators; detecting zero-contrast text or hidden styling
triggers automated spam disqualification and candidate blacklisting.
"""

import re
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("ATSHackDetector")

# Regex patterns for deceptive CSS/HTML styling
WHITE_TEXT_PATTERNS = [
    re.compile(r'color\s*:\s*(#ffffff|#fff|white|rgb\s*\(\s*255\s*,\s*255\s*,\s*255\s*\)|rgba\s*\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0(\.0+)?\s*\))', re.IGNORECASE),
    re.compile(r'opacity\s*:\s*0(\.0+)?(?:\s*;|\s*$|\s*!)', re.IGNORECASE),
]

MICRO_FONT_PATTERNS = [
    re.compile(r'font-size\s*:\s*(?:0|0\.[0-5]|1)\s*(?:pt|px)', re.IGNORECASE),
    re.compile(r'font-size\s*:\s*0(?:\s*;|\s*$)', re.IGNORECASE),
]

OFFSCREEN_HIDDEN_PATTERNS = [
    re.compile(r'(?:left|top|right|bottom)\s*:\s*-\s*(?:999|9999|\d{4,})\s*px', re.IGNORECASE),
    re.compile(r'display\s*:\s*none', re.IGNORECASE),
    re.compile(r'visibility\s*:\s*hidden', re.IGNORECASE),
    re.compile(r'text-indent\s*:\s*-\s*(?:999|9999|\d{4,})\s*px', re.IGNORECASE),
]

# Zero-width / invisible Unicode codepoints: ZWSP, ZWNJ, ZWJ, BOM, Word Joiner
INVISIBLE_CHAR_REGEX = re.compile(r'[\u200B\u200C\u200D\uFEFF\u2060]')


def detect_ats_hacks(
    text: str,
    raw_markup: Optional[str] = None
) -> Dict[str, Any]:
    """
    Audits document content and optional raw markup for deceptive ATS bypass hacks.

    :param text: Cleaned or extracted plain text from resume
    :param raw_markup: Optional HTML, CSS, or raw stream text from document parser
    :return: Audit report dictionary containing risk tier, penalty points, and detected traps
    """
    detected_traps: List[Dict[str, str]] = []
    remediation_advice: List[str] = []
    penalty = 0

    combined_markup = (raw_markup or "") + "\n" + (text or "")

    # 1. Check for White-on-White / Zero Opacity Text
    for pattern in WHITE_TEXT_PATTERNS:
        matches = pattern.findall(combined_markup)
        if matches:
            penalty += 45
            trap_msg = "Detected zero-contrast white text (#ffffff) or zero opacity style."
            detected_traps.append({
                "type": "white_font_stuffing",
                "severity": "CRITICAL",
                "detail": trap_msg
            })
            remediation_advice.append("Remove white-on-white text styling. Enterprise ATS engines parse graphics state and flag zero-contrast text as spam.")
            break

    # 2. Check for Micro-Fonts (< 1pt or 0px)
    for pattern in MICRO_FONT_PATTERNS:
        matches = pattern.findall(combined_markup)
        if matches:
            penalty += 40
            trap_msg = "Detected micro-font styling (font-size <= 1px/0.5pt) designed to hide text from visual inspection."
            detected_traps.append({
                "type": "micro_font_hidden",
                "severity": "CRITICAL",
                "detail": trap_msg
            })
            remediation_advice.append("Ensure all document typography uses standard legible font sizes (10pt-12pt for body text).")
            break

    # 3. Check for Off-Screen / Hidden Positioning
    for pattern in OFFSCREEN_HIDDEN_PATTERNS:
        matches = pattern.findall(combined_markup)
        if matches:
            penalty += 35
            trap_msg = "Detected off-screen positioning or hidden display elements (display:none / left: -9999px)."
            detected_traps.append({
                "type": "offscreen_hidden_element",
                "severity": "HIGH",
                "detail": trap_msg
            })
            remediation_advice.append("Remove hidden or off-canvas CSS containers. ATS parsers extract all DOM content and cross-reference visible bounding boxes.")
            break

    # 4. Check for Invisible Unicode Zero-Width Characters
    if text:
        invis_chars = INVISIBLE_CHAR_REGEX.findall(text)
        invis_count = len(invis_chars)
        if invis_count > 10:
            p = min(30, invis_count * 2)
            penalty += p
            detected_traps.append({
                "type": "invisible_unicode_injection",
                "severity": "MEDIUM",
                "detail": f"Detected {invis_count} invisible zero-width Unicode characters (\\u200B-\\uFEFF)."
            })
            remediation_advice.append("Sanitize document to remove invisible zero-width Unicode characters that distort search tokenization.")

    # 5. Check for Verbatim Keyword Stuffing Repetition
    if text:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        if words:
            # Check 4+ consecutive identical words
            consecutive_dup = re.search(r'\b([a-zA-Z]{3,})\b(?:\s+\1\b){3,}', text, re.IGNORECASE)
            if consecutive_dup:
                penalty += 35
                repeated_word = consecutive_dup.group(1)
                detected_traps.append({
                    "type": "consecutive_keyword_stuffing",
                    "severity": "CRITICAL",
                    "detail": f"Detected consecutive repeated keyword spam: '{repeated_word}'."
                })
                remediation_advice.append("Eliminate repeated keyword lists. Ground skills in contextual XYZ achievement bullets.")

            # Check unpunctuated keyword dump blocks (> 20 comma-separated keywords without verbs)
            comma_blocks = re.findall(r'(?:[a-zA-Z\s]{2,20},){8,}', text)
            for block in comma_blocks:
                token_count = len(block.split(','))
                if token_count >= 15:
                    penalty += 20
                    detected_traps.append({
                        "type": "unpunctuated_keyword_dump",
                        "severity": "MEDIUM",
                        "detail": f"Detected unpunctuated keyword dump block with {token_count} comma-separated terms."
                    })
                    remediation_advice.append("Format skills into categorized sections rather than flat keyword dumps.")
                    break

    # Calculate final hack risk score (100 = pristine, 0 = severe hack exploitation)
    hack_risk_score = max(0, 100 - penalty)
    is_flagged = len(detected_traps) > 0

    if hack_risk_score >= 85:
        disqualification_risk = "None" if not is_flagged else "Low"
    elif hack_risk_score >= 60:
        disqualification_risk = "Medium"
    else:
        disqualification_risk = "Critical"

    clean_text_certified = hack_risk_score >= 85 and not any(
        t["severity"] == "CRITICAL" for t in detected_traps
    )

    return {
        "hack_risk_score": hack_risk_score,
        "is_flagged": is_flagged,
        "disqualification_risk": disqualification_risk,
        "clean_text_certified": clean_text_certified,
        "trap_count": len(detected_traps),
        "detected_traps": detected_traps,
        "remediation_advice": remediation_advice
    }
