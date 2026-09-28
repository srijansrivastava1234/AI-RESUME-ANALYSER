"""
Schema Exporter and ATS Rule Configuration Serializer.
Provides utilities to export ATS scoring rules, Pydantic schemas, and OpenAPI specifications.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

DEFAULT_EXPORT_RULES = {
    "version": "3.3.0",
    "metadata": {
        "engine": "Enterprise ATS Resume Analyzer",
        "compliance": ["NYC LL 144", "EEOC Uniform Guidelines", "EU AI Act Article 14"],
        "scoring_algorithms": ["Okapi BM25+", "Google X-Y-Z", "Recursive XY-Cut Linearization"]
    },
    "scoring_weights": {
        "bm25_lexical_weight": 0.25,
        "xyz_impact_weight": 0.25,
        "action_verbs_weight": 0.15,
        "section_flow_weight": 0.15,
        "contact_hygiene_weight": 0.10,
        "format_integrity_weight": 0.10
    },
    "thresholds": {
        "min_passing_score": 75.0,
        "seniority_years": {
            "entry": 0,
            "mid": 3,
            "senior": 6,
            "staff": 10,
            "principal": 15
        },
        "target_page_budget": {
            "entry_mid": 1,
            "senior_lead": 2,
            "executive": 3
        }
    }
}


def export_ats_rules_schema(output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Exports the comprehensive ATS rule definitions and scoring weights schema.
    If output_path is provided, writes the serialized JSON schema to disk.
    """
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "ATSResumeAnalyzerRulesConfiguration",
        "type": "object",
        "properties": {
            "version": {"type": "string"},
            "metadata": {
                "type": "object",
                "properties": {
                    "engine": {"type": "string"},
                    "compliance": {"type": "array", "items": {"type": "string"}},
                    "scoring_algorithms": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["engine", "compliance", "scoring_algorithms"]
            },
            "scoring_weights": {
                "type": "object",
                "properties": {
                    "bm25_lexical_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "xyz_impact_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "action_verbs_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "section_flow_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "contact_hygiene_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "format_integrity_weight": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                },
                "required": [
                    "bm25_lexical_weight",
                    "xyz_impact_weight",
                    "action_verbs_weight",
                    "section_flow_weight",
                    "contact_hygiene_weight",
                    "format_integrity_weight"
                ]
            },
            "thresholds": {"type": "object"}
        },
        "required": ["version", "metadata", "scoring_weights", "thresholds"],
        "default_config": DEFAULT_EXPORT_RULES
    }

    if output_path:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)

    return schema


def validate_custom_rules_schema(config_dict: Dict[str, Any]) -> bool:
    """
    Validates a user-supplied custom rules configuration against required schema weights.
    Returns True if valid, raises ValueError otherwise.
    """
    if not isinstance(config_dict, dict):
        raise ValueError("Configuration must be a dictionary")

    weights = config_dict.get("scoring_weights")
    if not isinstance(weights, dict):
        raise ValueError("Configuration missing 'scoring_weights' object")

    required_keys = [
        "bm25_lexical_weight",
        "xyz_impact_weight",
        "action_verbs_weight",
        "section_flow_weight",
        "contact_hygiene_weight",
        "format_integrity_weight"
    ]

    for k in required_keys:
        if k not in weights:
            raise ValueError(f"Missing required scoring weight: {k}")
        if not isinstance(weights[k], (int, float)) or weights[k] < 0:
            raise ValueError(f"Weight {k} must be a non-negative number")

    total_weight = sum(float(weights[k]) for k in required_keys)
    if not (0.99 <= total_weight <= 1.01):
        raise ValueError(f"Scoring weights must sum to 1.0 (actual sum: {total_weight:.3f})")

    return True
