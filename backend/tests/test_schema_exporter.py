"""
Unit tests for schema_exporter module.
Validates ATS rule serialization, custom rule schema validation, and JSON Resume conversion.
"""

import json
import pytest
from app.schema_exporter import (
    DEFAULT_EXPORT_RULES,
    export_ats_rules_schema,
    validate_custom_rules_schema,
    export_json_resume_schema,
)


def test_export_ats_rules_schema_in_memory():
    schema = export_ats_rules_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == "ATSResumeAnalyzerRulesConfiguration"
    assert "scoring_weights" in schema["properties"]
    assert schema["default_config"] == DEFAULT_EXPORT_RULES


def test_export_ats_rules_schema_to_disk(tmp_path):
    target = tmp_path / "subdir" / "rules_schema.json"
    schema = export_ats_rules_schema(output_path=str(target))
    assert target.exists()

    with open(target, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == schema
    assert loaded["default_config"]["version"] == "3.3.0"


def test_validate_custom_rules_schema_success():
    valid_config = {
        "scoring_weights": {
            "bm25_lexical_weight": 0.20,
            "xyz_impact_weight": 0.30,
            "action_verbs_weight": 0.15,
            "section_flow_weight": 0.15,
            "contact_hygiene_weight": 0.10,
            "format_integrity_weight": 0.10,
        }
    }
    assert validate_custom_rules_schema(valid_config) is True


def test_validate_custom_rules_schema_invalid_types():
    with pytest.raises(ValueError, match="Configuration must be a dictionary"):
        validate_custom_rules_schema(["not", "a", "dict"])

    with pytest.raises(ValueError, match="missing 'scoring_weights' object"):
        validate_custom_rules_schema({"version": "1.0"})

    with pytest.raises(ValueError, match="Missing required scoring weight"):
        validate_custom_rules_schema({"scoring_weights": {"bm25_lexical_weight": 1.0}})


def test_validate_custom_rules_schema_invalid_weights():
    base_weights = {
        "bm25_lexical_weight": 0.25,
        "xyz_impact_weight": 0.25,
        "action_verbs_weight": 0.15,
        "section_flow_weight": 0.15,
        "contact_hygiene_weight": 0.10,
        "format_integrity_weight": -0.10,
    }
    with pytest.raises(ValueError, match="must be a non-negative number"):
        validate_custom_rules_schema({"scoring_weights": base_weights})

    # Weight sum != 1.0
    bad_sum = dict(base_weights)
    bad_sum["format_integrity_weight"] = 0.50
    with pytest.raises(ValueError, match="Scoring weights must sum to 1.0"):
        validate_custom_rules_schema({"scoring_weights": bad_sum})


def test_export_json_resume_schema_with_string_skills_and_fallbacks():
    resume_data = {
        "contact": {
            "name": "Alex Mercer",
            "title": "Systems Lead",
            "website": "https://mercer.dev",
            "linkedin": "https://linkedin.com/in/alexmercer",
            "github": "https://github.com/alexmercer",
            "city": "Austin",
            "country": "USA",
        },
        "summary": "Distributed systems specialist.",
        "skills": ["Rust", "Distributed Systems", {"category": "Tools", "skills": ["Docker"]}],
        "work_experience": [
            {
                "company": "Proto Corp",
                "role": "Lead Architect",
                "start_date": "2021-01",
                "highlights": ["Zero-downtime database migration"],
            }
        ],
        "education": [
            {
                "school": "UT Austin",
                "field": "CS",
                "start_date": "2016",
                "end_date": "2020",
            }
        ],
    }

    schema = export_json_resume_schema(resume_data)
    assert schema["basics"]["name"] == "Alex Mercer"
    assert schema["basics"]["url"] == "https://linkedin.com/in/alexmercer"
    assert len(schema["basics"]["profiles"]) == 2
    assert schema["basics"]["profiles"][0]["network"] == "LinkedIn"
    assert schema["basics"]["profiles"][1]["network"] == "GitHub"
    assert schema["basics"]["location"]["city"] == "Austin"
    assert len(schema["skills"]) == 3
    assert schema["skills"][0]["name"] == "Skills"
    assert schema["skills"][0]["keywords"] == ["Rust"]
    assert schema["skills"][2]["name"] == "Tools"
    assert schema["work"][0]["name"] == "Proto Corp"
    assert schema["work"][0]["position"] == "Lead Architect"
    assert schema["education"][0]["institution"] == "UT Austin"
