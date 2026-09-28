"""
Unit tests for schema_exporter and rule configuration validation.
"""

import pytest
import os
import tempfile
from app.schema_exporter import (
    DEFAULT_EXPORT_RULES,
    export_ats_rules_schema,
    validate_custom_rules_schema
)


def test_export_ats_rules_schema_structure():
    schema = export_ats_rules_schema()
    assert "$schema" in schema
    assert "properties" in schema
    assert "scoring_weights" in schema["properties"]
    assert schema["default_config"]["version"] == "3.3.0"


def test_export_ats_rules_schema_file_writing():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "rules_schema.json")
        schema = export_ats_rules_schema(output_path=out_file)
        assert os.path.exists(out_file)
        assert os.path.getsize(out_file) > 100


def test_validate_custom_rules_schema_valid():
    valid_cfg = {
        "scoring_weights": {
            "bm25_lexical_weight": 0.25,
            "xyz_impact_weight": 0.25,
            "action_verbs_weight": 0.15,
            "section_flow_weight": 0.15,
            "contact_hygiene_weight": 0.10,
            "format_integrity_weight": 0.10
        }
    }
    assert validate_custom_rules_schema(valid_cfg) is True


def test_validate_custom_rules_schema_invalid_sum():
    invalid_cfg = {
        "scoring_weights": {
            "bm25_lexical_weight": 0.50,
            "xyz_impact_weight": 0.50,
            "action_verbs_weight": 0.50,
            "section_flow_weight": 0.15,
            "contact_hygiene_weight": 0.10,
            "format_integrity_weight": 0.10
        }
    }
    with pytest.raises(ValueError, match="must sum to 1.0"):
        validate_custom_rules_schema(invalid_cfg)


def test_validate_custom_rules_schema_missing_key():
    invalid_cfg = {
        "scoring_weights": {
            "bm25_lexical_weight": 0.50,
            "xyz_impact_weight": 0.50
        }
    }
    with pytest.raises(ValueError, match="Missing required scoring weight"):
        validate_custom_rules_schema(invalid_cfg)
