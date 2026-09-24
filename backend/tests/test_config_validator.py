"""
Unit tests for configuration and system environment validator.
"""

import pytest
from app.config_validator import validate_runtime_environment, get_system_health_report


def test_validate_runtime_environment_default():
    env = {}
    config = validate_runtime_environment(env)
    assert config["status"] == "HEALTHY"
    assert config["gemini_configured"] is False
    assert config["api_mode"] == "Deterministic Heuristic Offline"
    assert config["port"] == 8000
    assert config["is_port_valid"] is True


def test_validate_runtime_environment_configured():
    env = {
        "GEMINI_API_KEY": "AIzaSyFakeKey12345",
        "PORT": "9000",
        "LOG_LEVEL": "DEBUG"
    }
    config = validate_runtime_environment(env)
    assert config["gemini_configured"] is True
    assert "Hybrid" in config["api_mode"]
    assert config["port"] == 9000
    assert config["log_level"] == "DEBUG"


def test_validate_runtime_invalid_port():
    env = {"PORT": "invalid_port"}
    config = validate_runtime_environment(env)
    assert config["port"] == 8000
    assert config["is_port_valid"] is False


def test_get_system_health_report():
    report = get_system_health_report({"GEMINI_API_KEY": "valid_key"})
    assert report["service"] == "AI Resume Analyser Backend"
    assert report["version"] == "3.1.0"
    assert report["status"] == "HEALTHY"
    assert report["runtime"]["ai_active"] is True
    assert report["runtime"]["heuristic_fallback_ready"] is True
