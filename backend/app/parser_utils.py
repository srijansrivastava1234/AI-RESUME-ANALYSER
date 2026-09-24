"""
High-Performance Parsing Utilities & Regex Compilation Cache.
Provides fast token normalization, cached string sanitization, and unicode control character stripping.
"""

import re
import unicodedata
from functools import lru_cache
from typing import List, Tuple

# Precompiled regex patterns for maximum parsing throughput
RE_EXTRA_WHITESPACE = re.compile(r"[ \t\u00A0\u1680\u2000-\u200A\u202F\u205F\u3000]+")
RE_NEWLINES = re.compile(r"(\r\n|\r|\n){3,}")
RE_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
RE_BULLET_PREFIX = re.compile(r"^[\s\t]*([•\-\*–—▪►●✓✔]|(?:\d+[\.\)]))\s*")
RE_TOKEN = re.compile(r"(?:c\+\+|c\#|\.net|\b[a-zA-Z0-9_\-\.]+\b)", re.IGNORECASE)


@lru_cache(maxsize=4096)
def sanitize_text_cached(text: str) -> str:
    """
    Strips non-printable control characters, normalizes Unicode forms to NFC,
    and consolidates excessive horizontal and vertical whitespace.
    """
    if not text:
        return ""
    # Normalize unicode to standard composite characters
    normalized = unicodedata.normalize("NFC", text)
    # Strip dangerous ASCII control codes
    stripped = RE_CONTROL_CHARS.sub("", normalized)
    # Line by line whitespace clean
    lines = [RE_EXTRA_WHITESPACE.sub(" ", line).strip() for line in stripped.splitlines()]
    clean_text = "\n".join(lines)
    # Normalize excessive vertical gaps
    cleaned = RE_NEWLINES.sub("\n\n", clean_text)
    return cleaned.strip()


def fast_tokenize(text: str) -> List[str]:
    """
    Extracts alphanumeric and symbol-bearing tokens (e.g., C++, C#, .NET, Node.js)
    with zero string allocation overhead.
    """
    if not text:
        return []
    return [t.lower() for t in RE_TOKEN.findall(text)]


def strip_bullet_prefix(line: str) -> Tuple[bool, str]:
    """
    Detects and removes leading bullet markers, returning (was_bullet, cleaned_text).
    """
    if not line:
        return False, ""
    match = RE_BULLET_PREFIX.match(line)
    if match:
        return True, line[match.end():].strip()
    return False, line.strip()
