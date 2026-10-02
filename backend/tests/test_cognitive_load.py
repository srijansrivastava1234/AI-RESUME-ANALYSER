"""Unit tests for Cognitive Load & Readability Index Engine."""

import pytest
from app.cognitive_load import evaluate_cognitive_load, _count_syllables_word


def test_syllable_counter():
    assert _count_syllables_word("fast") == 1
    assert _count_syllables_word("system") == 2
    assert _count_syllables_word("architecture") == 4
    assert _count_syllables_word("internationalization") >= 6
    assert _count_syllables_word("") == 0


def test_empty_text():
    res = evaluate_cognitive_load("")
    assert res["cognitive_load_score"] == 0.0
    assert res["skimmability_rating"] == "UNEVALUATED"


def test_balanced_resume_text():
    text = """
    - Engineered scalable microservices using Python and FastAPI, improving latency by 35%.
    - Designed database schema in PostgreSQL and reduced query execution time from 200ms to 45ms.
    - Mentored four junior software engineers and led agile sprint planning meetings.
    """
    res = evaluate_cognitive_load(text)
    assert 5.0 <= res["gunning_fog_index"] <= 20.0
    assert res["cognitive_load_score"] >= 60.0
    assert res["skimmability_rating"] in ["OPTIMAL_SKIMMABILITY", "GOOD_SKIMMABILITY", "MODERATE_COGNITIVE_STRAIN"]
    assert res["total_words"] > 20
    assert res["total_sentences"] >= 3


def test_overly_complex_jargon():
    text = """
    Incomprehensibly institutionalized multidimensional compartmentalization of extraordinarily parameterized internationalization infrastructural architectures facilitating counterrevolutionary interoperability.
    """
    res = evaluate_cognitive_load(text)
    assert res["gunning_fog_index"] >= 15.0
    assert res["cognitive_load_score"] < 70.0
    assert any("High Gunning Fog" in r or "polysyllable" in r for r in res["recommendations"])
