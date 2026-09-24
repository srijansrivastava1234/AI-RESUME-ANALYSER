"""
End-to-End Architectural Integrity Test Suite for Top 9 Pillars.
Validates mathematical soundness, deterministic edge cases, and module conformance across all 9 core innovations.
"""

import pytest
from app.compliance import audit_ats_compliance, extract_resume_bullets, filter_false_positive_metrics
from app.bm25_scorer import compute_bm25_plus, calculate_idf, tokenize
from app.font_integrity import normalize_typographic_ligatures, audit_font_cmap_integrity
from app.chronology import audit_career_chronology
from app.redaction import anonymize_resume_for_blind_audit
from app.skill_classifier import audit_skills, classify_single_skill
from app.resume_builder import parse_resume_to_structured_json, format_structured_resume_to_plain_text


class TestTop9ArchitecturalPillars:
    """Rigorous validation of the 9 Flagship Technical Pillars."""

    # Pillar 1 & 2: Full-Stack Compliance & Scoring Engine
    def test_pillar_1_and_2_compliance_engine(self):
        sample_resume = (
            "John Doe\n"
            "Software Engineer | john.doe@example.com | (555) 123-4567\n"
            "Experience\n"
            "Senior Software Engineer at Tech Corp\n"
            "Jan 2021 - Present\n"
            "- Spearheaded microservices migration using Python and FastAPI, reducing latency by 45% and saving $120k annually.\n"
            "- Optimized PostgreSQL database queries, improving throughput by 30% across 50,000 daily active users.\n"
            "Education\n"
            "B.S. in Computer Science, University of Technology (2016 - 2020)\n"
            "Skills: Python, FastAPI, Docker, PostgreSQL, React, Git, AWS\n"
        )
        result = audit_ats_compliance(sample_resume, job_description="Looking for Python FastAPI PostgreSQL engineer")
        assert result is not None
        assert "composite_score" in result
        assert 0 <= result["composite_score"] <= 100
        assert result["letter_grade"] in ["A+", "A", "B", "C", "D"]
        assert "itemized_audit_trail" in result
        assert len(result["itemized_audit_trail"]) == 4

    # Pillar 3: Okapi BM25+ Scorer with Saturation & Penalty
    def test_pillar_3_bm25_plus_retrieval(self):
        doc = "Python developer building distributed APIs with FastAPI and Docker containers."
        keywords = ["Python", "FastAPI", "Docker", "Kubernetes"]
        res = compute_bm25_plus(doc, keywords)
        assert res is not None
        assert res["raw_bm25_score"] > 0
        assert res["normalized_score"] > 0
        assert res["matched_keywords"] >= 3
        assert len(res["stuffed_terms"]) == 0

    # Pillar 4: Layout & Scanline Linearization Check
    def test_pillar_4_false_positive_metrics_filter(self):
        bullet = "Upgraded to Python 3.12 on port 8080 complying with ISO 27001 achieving 100% test coverage."
        raw_metrics = ["3.12", "8080", "27001", "100%"]
        filtered = filter_false_positive_metrics(bullet, raw_metrics)
        assert "8080" not in filtered
        assert any("100%" in m for m in filtered)

    # Pillar 5: Font Integrity & Ligature Normalization
    def test_pillar_5_font_and_ligature_normalization(self):
        corrupt_text = "The ef\ufb01cient of\ufb02ine \uE001 sys\ufb01tem with \uFFFD replacement."
        audit = audit_font_cmap_integrity(corrupt_text)
        assert audit is not None
        assert audit["font_health_score"] < 100
        assert audit["ligature_count"] >= 2
        assert audit["pua_glyph_count"] >= 1
        normalized, _, _ = normalize_typographic_ligatures(corrupt_text)
        assert "efficient" in normalized
        assert "offline" in normalized

    # Pillar 6: Career Chronology & Gap Detection
    def test_pillar_6_career_chronology(self):
        resume_text = (
            "Experience\n"
            "Software Engineer at Alpha Inc\n"
            "Jan 2019 - Dec 2020\n"
            "- Built backend services.\n\n"
            "Senior Engineer at Beta Corp\n"
            "Jun 2021 - Present\n"
            "- Led cloud migration.\n"
        )
        chronology = audit_career_chronology(resume_text)
        assert chronology is not None
        assert chronology["detected_roles_count"] >= 1
        assert "career_gaps" in chronology
        assert chronology["total_experience_years"] > 0

    # Pillar 7: PII Redactor for Blind Reviews (NYC LL 144)
    def test_pillar_7_pii_redaction(self):
        raw_text = "Alice Johnson, reachable at alice@example.com or (415) 555-2671, graduated in 2012."
        redacted = anonymize_resume_for_blind_audit(raw_text)
        assert redacted is not None
        assert "alice@example.com" not in redacted["sanitized_text"]
        assert "(415) 555-2671" not in redacted["sanitized_text"]
        assert "[EMAIL REDACTED]" in redacted["sanitized_text"]
        assert redacted["safe_harbor_certified"] is True

    # Pillar 8: Hard vs Soft Skill Taxonomy Classifier
    def test_pillar_8_skill_taxonomy(self):
        skills_list = ["Python", "Kubernetes", "PostgreSQL", "TypeScript", "leadership", "communication", "team player"]
        audit = audit_skills(skills_list)
        assert audit is not None
        assert audit["hard_skills_count"] >= 3
        assert audit["soft_skills_count"] >= 2
        assert 0.0 <= audit["hard_ratio"] <= 100.0
        assert 0.0 <= audit["credibility_index"] <= 100.0

    # Pillar 9: Structural Resume Compiler & Text Generator
    def test_pillar_9_structured_resume_compiler(self):
        raw_text = (
            "ALEX MERCER\n"
            "alex.mercer@example.com | (555) 123-4567 | San Francisco, CA\n\n"
            "PROFESSIONAL SUMMARY\n"
            "Full-stack engineer with 6+ years building resilient cloud web services.\n\n"
            "WORK EXPERIENCE\n"
            "Lead Architect | Cloud Systems | 2021 - Present\n"
            "- Architected event-driven microservices serving 10M+ daily events.\n\n"
            "EDUCATION\n"
            "B.S. in Computer Science | Stanford University | 2015 - 2019\n\n"
            "TECHNICAL SKILLS\n"
            "Python, FastAPI, Docker, PostgreSQL, Kafka, Kubernetes, AWS\n"
        )
        structured = parse_resume_to_structured_json(raw_text)
        assert structured is not None
        assert "ALEX MERCER" in structured["contact"]["full_name"] or "Alex Mercer" in structured["contact"]["full_name"]
        assert len(structured["experience"]) >= 1
        plain_text = format_structured_resume_to_plain_text(structured)
        assert "ALEX MERCER" in plain_text
        assert "EXPERIENCE" in plain_text
