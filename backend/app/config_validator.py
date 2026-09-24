"""
System Configuration & Runtime Environment Validator.
Provides diagnostic environment auditing, API key readiness checks,
and platform health telemetry.
"""

import os
from typing import Dict, Any, Optional


def validate_runtime_environment(env_dict: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Validates current operating environment variables and returns system readiness metadata.
    """
    env = env_dict if env_dict is not None else os.environ

    gemini_key = env.get("GEMINI_API_KEY", "").strip()
    is_gemini_configured = bool(gemini_key and gemini_key != "your_gemini_api_key_here")

    port_str = env.get("PORT", "8000")
    try:
        port = int(port_str)
        is_port_valid = 1 <= port <= 65535
    except ValueError:
        port = 8000
        is_port_valid = False

    log_level = env.get("LOG_LEVEL", "INFO").upper()
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    is_log_level_valid = log_level in valid_log_levels

    return {
        "gemini_configured": is_gemini_configured,
        "api_mode": "Hybrid (AI + Heuristic Fallback)" if is_gemini_configured else "Deterministic Heuristic Offline",
        "port": port,
        "is_port_valid": is_port_valid,
        "log_level": log_level if is_log_level_valid else "INFO",
        "version": "3.1.0",
        "status": "HEALTHY",
        "supported_upload_types": ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"],
        "max_upload_size_mb": 10
    }


def get_system_health_report(env_dict: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Generates a structured system telemetry report for health check endpoints.
    """
    config = validate_runtime_environment(env_dict)
    return {
        "service": "AI Resume Analyser Backend",
        "version": config["version"],
        "status": config["status"],
        "runtime": {
            "mode": config["api_mode"],
            "ai_active": config["gemini_configured"],
            "heuristic_fallback_ready": True
        },
        "limits": {
            "max_file_size_mb": config["max_upload_size_mb"],
            "analysis_rate_limit": "10/minute",
            "batch_compare_rate_limit": "5/minute"
        }
    }
