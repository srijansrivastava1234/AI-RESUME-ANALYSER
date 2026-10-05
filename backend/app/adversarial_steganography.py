"""Advanced Adversarial Steganography & Homoglyph Attack Detector.

Audits resumes for complex evasion attacks:
1. Zero-Width Binary Steganography (ZWSP/ZWNJ binary-encoded payload extraction).
2. Homoglyph / Mixed-Script Spoofing (Cyrillic/Greek lookalikes in Latin technical terms).
3. Invisible Soft-Hyphen and Zero-Width Word Fragmentation attacks.
4. Deterministic Canonical Normalization & Sanitization.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Tuple

# Mapping of common Cyrillic and Greek homoglyphs to canonical Latin characters
HOMOGLYPH_MAP = {
    # Cyrillic small lookalikes
    '\u0430': 'a',  # Cyrillic small a
    '\u0441': 'c',  # Cyrillic small es (c)
    '\u0435': 'e',  # Cyrillic small ie (e)
    '\u0456': 'i',  # Cyrillic small Byelorussian-Ukrainian i
    '\u0458': 'j',  # Cyrillic small je (j)
    '\u043e': 'o',  # Cyrillic small o
    '\u0440': 'p',  # Cyrillic small er (p)
    '\u0455': 's',  # Cyrillic small dze (s)
    '\u0445': 'x',  # Cyrillic small ha (x)
    '\u0443': 'y',  # Cyrillic small u (y)
    # Cyrillic capital lookalikes
    '\u0410': 'A',
    '\u0412': 'B',
    '\u0421': 'C',
    '\u0415': 'E',
    '\u041d': 'H',
    '\u0406': 'I',
    '\u0408': 'J',
    '\u041a': 'K',
    '\u041c': 'M',
    '\u041e': 'O',
    '\u0420': 'P',
    '\u0422': 'T',
    '\u0425': 'X',
    # Greek lookalikes
    '\u0391': 'A',
    '\u0392': 'B',
    '\u0395': 'E',
    '\u0397': 'H',
    '\u0399': 'I',
    '\u039a': 'K',
    '\u039c': 'M',
    '\u039d': 'N',
    '\u039f': 'O',
    '\u03a1': 'P',
    '\u03a4': 'T',
    '\u03a7': 'X',
    '\u03bf': 'o',
}

ZWSP = '\u200B'
ZWNJ = '\u200C'
ZWJ = '\u200D'


def decode_zero_width_binary_payload(text: str) -> List[str]:
    """
    Extracts and decodes hidden binary payloads encoded using zero-width characters:
    - \u200B (ZWSP) -> 0
    - \u200C (ZWNJ) -> 1
    - \u200D (ZWJ) or whitespace -> byte boundary
    """
    decoded_payloads: List[str] = []
    
    # Find contiguous sequences of zero-width characters (at least 8 bits)
    zw_matches = re.findall(r'[\u200B\u200C\u200D\uFEFF]{8,}', text)
    
    for seq in zw_matches:
        # Translate to binary bitstream
        bits = []
        for ch in seq:
            if ch == ZWSP or ch == '\uFEFF':
                bits.append('0')
            elif ch == ZWNJ:
                bits.append('1')
            elif ch == ZWJ:
                # Delimiter or spacer
                pass

        bit_string = "".join(bits)
        if len(bit_string) >= 8:
            chars = []
            for i in range(0, len(bit_string) - (len(bit_string) % 8), 8):
                byte = bit_string[i:i+8]
                try:
                    val = int(byte, 2)
                    if 32 <= val <= 126:  # Printable ASCII
                        chars.append(chr(val))
                except Exception:
                    pass
            if chars:
                decoded = "".join(chars)
                if len(decoded.strip()) > 0:
                    decoded_payloads.append(decoded)

    return decoded_payloads


def detect_homoglyph_substitutions(text: str) -> List[Dict[str, Any]]:
    """
    Detects words containing suspicious mixed scripts (e.g. Latin word containing Cyrillic/Greek lookalikes).
    """
    suspicious_words: List[Dict[str, Any]] = []
    words = text.split()

    for word in words:
        clean_word = re.sub(r'[^\w]', '', word)
        if not clean_word:
            continue

        has_latin = bool(re.search(r'[a-zA-Z]', clean_word))
        has_homoglyph = any(ch in HOMOGLYPH_MAP for ch in clean_word)

        if has_latin and has_homoglyph:
            # Reconstruct intended word
            canonical = "".join(HOMOGLYPH_MAP.get(ch, ch) for ch in clean_word)
            spoofed_chars = [
                {"char": ch, "codepoint": f"U+{ord(ch):04X}", "replaces": HOMOGLYPH_MAP[ch]}
                for ch in clean_word if ch in HOMOGLYPH_MAP
            ]
            suspicious_words.append({
                "original": clean_word,
                "canonical": canonical,
                "spoofed_chars": spoofed_chars
            })

    return suspicious_words


def sanitize_adversarial_text(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Performs deterministic canonical normalization:
    1. Replaces homoglyphs with standard ASCII counterparts.
    2. Strips zero-width characters and soft hyphens.
    3. Normalizes Unicode to NFKC.
    
    Returns:
        Tuple of (sanitized_text, audit_report)
    """
    if not text:
        return "", {
            "is_adversarial": False,
            "threat_score": 0,
            "steganography_detected": False,
            "homoglyphs_detected": 0,
            "decoded_payloads": [],
            "sanitized_length": 0
        }

    # 1. Steganography detection
    decoded_payloads = decode_zero_width_binary_payload(text)
    
    # 2. Homoglyph detection
    homoglyphs = detect_homoglyph_substitutions(text)

    # 3. Canonical replacement
    sanitized = text
    # Replace homoglyphs
    for h in homoglyphs:
        sanitized = re.sub(re.escape(h["original"]), h["canonical"], sanitized)

    # Strip zero-width and invisible characters
    sanitized = re.sub(r'[\u200B-\u200F\uFEFF\u2060\u00AD\u180E]', '', sanitized)
    
    # Normalize NFKC
    sanitized = unicodedata.normalize("NFKC", sanitized)

    # Calculate threat score
    threat_score = 0
    if decoded_payloads:
        threat_score += 60
    if homoglyphs:
        threat_score += min(40, len(homoglyphs) * 15)

    threat_score = min(100, threat_score)

    report = {
        "is_adversarial": threat_score >= 30,
        "threat_score": threat_score,
        "steganography_detected": len(decoded_payloads) > 0,
        "decoded_payloads": decoded_payloads,
        "homoglyphs_detected": len(homoglyphs),
        "homoglyph_details": homoglyphs,
        "original_length": len(text),
        "sanitized_length": len(sanitized)
    }

    return sanitized, report
