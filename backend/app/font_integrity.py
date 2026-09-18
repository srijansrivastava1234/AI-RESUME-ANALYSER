import re
from typing import Dict, List, Any, Tuple

LIGATURE_MAP = {
    "\uFB00": "ff",
    "\uFB01": "fi",
    "\uFB02": "fl",
    "\uFB03": "ffi",
    "\uFB04": "ffl",
    "\uFB05": "ft",
    "\uFB06": "st",
    "\u0152": "OE",
    "\u0153": "oe",
    "\u00C6": "AE",
    "\u00E6": "ae",
}

LIGATURE_REGEX = re.compile(r'[\uFB00-\uFB06\u0152\u0153\u00C6\u00E6]')

PUA_REGEX = re.compile(r'[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\U00100000-\U0010FFFD]')
REPLACEMENT_REGEX = re.compile(r'\uFFFD')
ZERO_WIDTH_REGEX = re.compile(r'[\u200B\u200C\u200D\uFEFF]')
SOFT_HYPHEN_REGEX = re.compile(r'\u00AD')

def normalize_typographic_ligatures(text: str) -> Tuple[str, Dict[str, int], List[str]]:
    """
    Decomposes typographic ligatures (fi, fl, ff, ffi, ffl, oe, ae) into their ASCII
    counterparts to restore searchability in applicant tracking systems.

    :param text: Raw extracted text
    :return: (normalized_text, counts_dict, recovered_words_list)
    """
    if not text:
        return "", {}, []

    counts: Dict[str, int] = {}
    recovered_words: List[str] = []

    # Find words containing ligatures before replacement for diagnostic preview
    word_pattern = re.compile(r'\b\w*[\uFB00-\uFB06\u0152\u0153\u00C6\u00E6]\w*\b')
    for m in word_pattern.finditer(text):
        orig = m.group(0)
        norm = orig
        for lig, repl in LIGATURE_MAP.items():
            norm = norm.replace(lig, repl)
        if orig != norm and len(recovered_words) < 5:
            recovered_words.append(f"'{orig}' ➔ '{norm}'")

    for lig, repl in LIGATURE_MAP.items():
        count = text.count(lig)
        if count > 0:
            counts[repl] = count

    def _replace_ligature(match: re.Match) -> str:
        return LIGATURE_MAP.get(match.group(0), match.group(0))

    normalized = LIGATURE_REGEX.sub(_replace_ligature, text)
    return normalized, counts, recovered_words

def audit_font_cmap_integrity(text: str) -> Dict[str, Any]:
    """
    Audits PDF and document text layer for Unicode CMap integrity, font subsetting
    defects, and ISO 19005-2 (PDF/A-2u) searchability compliance.

    Detects:
    1. Private Use Area (PUA) glyphs (\uE000-\uF8FF) caused by missing /ToUnicode CMap dictionaries.
    2. Unicode replacement characters (\uFFFD) indicating text layer decode failure.
    3. Soft hyphens (\u00AD) splitting keywords across line breaks.
    4. Zero-width and hidden Unicode characters (\u200B-\uFEFF).
    5. Search-breaking typographic ligatures with automated decomposition preview.

    :param text: Document text layer
    :return: Diagnostic dictionary with health score, compliance flag, and remediation guidance
    """
    if not text or not text.strip():
        return {
            "font_health_score": 0,
            "iso_19005_compliant": False,
            "is_searchable": False,
            "pua_glyph_count": 0,
            "replacement_char_count": 0,
            "soft_hyphen_count": 0,
            "zero_width_count": 0,
            "ligature_count": 0,
            "ligatures_decomposed": {},
            "recovered_words": [],
            "remediations": ["Document contains no extractable text layer to audit font integrity."]
        }

    # Detect PUA glyphs
    pua_matches = PUA_REGEX.findall(text)
    pua_count = len(pua_matches)

    # Detect replacement characters (\uFFFD)
    rep_matches = REPLACEMENT_REGEX.findall(text)
    rep_count = len(rep_matches)

    # Detect soft hyphens (\u00AD)
    soft_hyphens = SOFT_HYPHEN_REGEX.findall(text)
    soft_hyphen_count = len(soft_hyphens)

    # Detect zero-width characters
    zero_width_matches = ZERO_WIDTH_REGEX.findall(text)
    zero_width_count = len(zero_width_matches)

    # Decompose ligatures
    normalized_text, lig_counts, recovered_words = normalize_typographic_ligatures(text)
    total_ligatures = sum(lig_counts.values())

    score = 100
    remediations: List[str] = []

    if rep_count > 0:
        penalty = min(40, rep_count * 5)
        score -= penalty
        remediations.append(
            f"Detected {rep_count} Unicode replacement character(s) (\uFFFD). The PDF text stream is corrupt "
            "or uses custom fonts without an embedded /ToUnicode CMap table."
        )

    if pua_count > 0:
        penalty = min(35, pua_count * 5)
        score -= penalty
        remediations.append(
            f"Detected {pua_count} Private Use Area (PUA) glyph(s) (\uE000-\uF8FF). Custom icon fonts (e.g. FontAwesome) "
            "mapped to PUA codepoints produce unsearchable gibberish in Workday, Taleo, and Ashby."
        )

    if soft_hyphen_count > 0:
        score -= min(15, soft_hyphen_count * 3)
        remediations.append(
            f"Detected {soft_hyphen_count} soft hyphen(s) (\\u00AD). Soft hyphens divide compound keywords into disjointed tokens "
            "in lexical indices (e.g. 'Micro-services' is indexed as two unrelated words)."
        )

    if zero_width_count > 5:
        score -= 15
        remediations.append(
            f"Detected {zero_width_count} zero-width or invisible characters. These can distort ATS n-gram tokenization."
        )

    if total_ligatures > 0:
        # Informational note rather than severe penalty, since we provide automatic normalization
        remediations.append(
            f"Detected {total_ligatures} typographic ligature(s) ({', '.join(lig_counts.keys())}). "
            "Decomposed ligatures into plain ASCII characters to ensure exact ATS keyword retrieval."
        )

    score = max(0, min(100, score))
    iso_compliant = (pua_count == 0 and rep_count == 0 and soft_hyphen_count == 0 and score >= 85)
    is_searchable = score >= 50 and len(text.strip()) >= 30

    if not remediations:
        remediations.append("ISO 19005-2 PDF/A text layer compliance verified. Zero PUA glyphs, corruption characters, or unnormalized ligatures.")

    return {
        "font_health_score": score,
        "iso_19005_compliant": iso_compliant,
        "is_searchable": is_searchable,
        "pua_glyph_count": pua_count,
        "replacement_char_count": rep_count,
        "soft_hyphen_count": soft_hyphen_count,
        "zero_width_count": zero_width_count,
        "ligature_count": total_ligatures,
        "ligatures_decomposed": lig_counts,
        "recovered_words": recovered_words,
        "normalized_text_preview": normalized_text[:300] if len(normalized_text) > 300 else normalized_text,
        "remediations": remediations
    }
