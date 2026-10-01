import pytest
from app.dialect_checker import audit_dialect_and_voice

def test_empty_text():
    result = audit_dialect_and_voice("")
    assert result["predominant_dialect"] == "neutral"
    assert result["consistency_score"] == 100
    assert result["is_mixed"] is False
    assert result["passive_voice_count"] == 0

def test_pure_us_dialect():
    text = "Optimized database queries and analyzed user behavior to customize dashboard layout."
    result = audit_dialect_and_voice(text)
    assert result["predominant_dialect"] == "US"
    assert result["consistency_score"] == 100
    assert result["is_mixed"] is False
    assert "optimized" in result["detected_us_terms"]
    assert "analyzed" in result["detected_us_terms"]
    assert "behavior" in result["detected_us_terms"]
    assert "customize" in result["detected_us_terms"]
    assert result["normalization_to_uk"]["optimized"] == "optimised"

def test_pure_uk_dialect():
    text = "Optimised database queries and analysed user behaviour to customise dashboard layout."
    result = audit_dialect_and_voice(text)
    assert result["predominant_dialect"] == "UK"
    assert result["consistency_score"] == 100
    assert result["is_mixed"] is False
    assert "optimised" in result["detected_uk_terms"]
    assert result["normalization_to_us"]["optimised"] == "optimized"

def test_mixed_dialect_detection():
    text = "Optimized performance while maintaining defence mechanisms and colour scheme programmes."
    result = audit_dialect_and_voice(text)
    assert result["is_mixed"] is True
    assert result["us_term_count"] >= 1
    assert result["uk_term_count"] >= 1
    assert result["consistency_score"] < 100
    assert any("Mixed dialect detected" in r for r in result["recommendations"])

def test_passive_voice_detection():
    text = """
    The backend pipeline was developed by our engineering team.
    Microservices were executed on Kubernetes clusters.
    Engineered low-latency REST endpoints with FastAPI.
    """
    result = audit_dialect_and_voice(text)
    assert result["passive_voice_count"] >= 2
    assert len(result["passive_voice_snippets"]) >= 2
    assert any("passive voice" in r.lower() for r in result["recommendations"])
