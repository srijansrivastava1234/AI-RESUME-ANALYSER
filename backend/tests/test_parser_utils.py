"""
Unit tests for high-performance parser utilities and regex caching.
"""

import pytest
from app.parser_utils import sanitize_text_cached, fast_tokenize, strip_bullet_prefix


def test_sanitize_text_cached_empty_and_normal():
    assert sanitize_text_cached("") == ""
    raw = "  Hello   \t  World  \n\n\n\n  New Section  "
    sanitized = sanitize_text_cached(raw)
    assert sanitized == "Hello World\n\nNew Section"


def test_sanitize_text_cached_control_chars():
    corrupt = "Software\x00 Engineer\x08 with Python\x1F."
    clean = sanitize_text_cached(corrupt)
    assert clean == "Software Engineer with Python."


def test_fast_tokenize_symbols():
    text = "Proficient in C++, C#, .NET, Node.js, and Python 3.12."
    tokens = fast_tokenize(text)
    assert "c++" in tokens
    assert "c#" in tokens
    assert ".net" in tokens or "net" in tokens
    assert "node.js" in tokens
    assert "python" in tokens


def test_strip_bullet_prefix():
    is_bullet, text = strip_bullet_prefix("• Spearheaded cloud migration")
    assert is_bullet is True
    assert text == "Spearheaded cloud migration"

    is_bullet, text = strip_bullet_prefix("1. Architected backend microservices")
    assert is_bullet is True
    assert text == "Architected backend microservices"

    is_bullet, text = strip_bullet_prefix("- Implemented CI/CD pipeline")
    assert is_bullet is True
    assert text == "Implemented CI/CD pipeline"

    is_bullet, text = strip_bullet_prefix("Regular text line without bullet")
    assert is_bullet is False
    assert text == "Regular text line without bullet"
