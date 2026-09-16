import pytest
from app.token_density import audit_token_density, detect_language


def test_optimal_technical_density():
    text = """
    Architected and deployed distributed event-driven microservices using Python, FastAPI,
    and PostgreSQL. Reduced API latency by 45% and scaled cluster throughput to 25,000 requests
    per second on Amazon Web Services using Docker and Kubernetes.
    """
    result = audit_token_density(text)
    assert result["token_density_score"] >= 85
    assert result["verdict"] == "Optimal Technical Density"
    assert result["detected_language"] == "en"
    assert result["signal_to_noise_ratio"] >= 0.50
    assert result["type_token_ratio"] >= 0.35


def test_verbose_conversational_overload():
    verbose_text = """
    I was responsible for and I had to do all of the things because it was very important
    for our team and we were always doing what we could so that they would be happy with us
    and then we had to make sure that there were no problems when we were doing it.
    """
    result = audit_token_density(verbose_text)
    assert result["verdict"] == "Verbose / Conversational Overload"
    assert result["token_density_score"] <= 75
    assert result["signal_to_noise_ratio"] < 0.45
    assert any("filler words" in rec for rec in result["recommendations"])


def test_keyword_stuffing_low_ttr():
    stuffing_text = "python java docker kubernetes aws " * 15
    result = audit_token_density(stuffing_text)
    assert result["verdict"] == "Keyword Stuffing / Severe Repetition"
    assert result["type_token_ratio"] < 0.25
    assert result["token_density_score"] <= 70


def test_multilingual_spanish_detection():
    spanish_text = """
    Desarrollo de aplicaciones distribuidas con Python y bases de datos relacionales en la nube.
    Implementacion de microservicios para la reduccion de latencia en sistemas de alta escala.
    """
    result = audit_token_density(spanish_text)
    assert result["detected_language"] == "es"
    assert result["stopword_count"] > 0


def test_multilingual_german_detection():
    german_text = """
    Entwicklung von Softwarearchitekturen mit Python und relationalen Datenbanken in der Cloud.
    Optimierung der Systemleistung für verteilte Systeme mit hoher Verfügbarkeit und Skalierbarkeit.
    """
    result = audit_token_density(german_text)
    assert result["detected_language"] == "de"
    assert result["stopword_count"] > 0


def test_sparse_and_empty_text():
    sparse_res = audit_token_density("Hello world developer")
    assert sparse_res["verdict"] == "Sparse Text"

    empty_res = audit_token_density("")
    assert empty_res["verdict"] == "Empty Document"
    assert empty_res["token_density_score"] == 0
