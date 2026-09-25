import pytest
from app.hack_detector import detect_ats_hacks


def test_clean_resume_text():
    clean_text = """
    Jane Doe
    Senior Software Engineer
    Architected high-throughput distributed microservices using Python, FastAPI, and PostgreSQL,
    reducing P99 latency by 35% across 10M daily transactions.
    Led cross-functional team of 6 engineers to deploy Kubernetes clusters on AWS.
    """
    result = detect_ats_hacks(clean_text)
    assert result["hack_risk_score"] == 100
    assert result["is_flagged"] is False
    assert result["disqualification_risk"] == "None"
    assert result["clean_text_certified"] is True
    assert result["trap_count"] == 0
    assert len(result["detected_traps"]) == 0


def test_white_font_detection():
    markup = "<span style='color: #ffffff; background-color: #fff;'>Python Java Docker AWS</span>"
    result = detect_ats_hacks("Jane Doe Software Engineer", raw_markup=markup)
    assert result["hack_risk_score"] <= 55
    assert result["is_flagged"] is True
    assert result["disqualification_risk"] in ("Medium", "Critical")
    assert result["clean_text_certified"] is False
    assert any(t["type"] == "white_font_stuffing" for t in result["detected_traps"])


def test_zero_opacity_detection():
    markup = "<div style='opacity: 0;'>Kubernetes Terraform Docker Jenkins</div>"
    result = detect_ats_hacks("Clean resume body", raw_markup=markup)
    assert any(t["type"] == "white_font_stuffing" for t in result["detected_traps"])
    assert result["is_flagged"] is True


def test_micro_font_detection():
    markup = "<p style='font-size: 0.1pt'>hidden keyword spam</p>"
    result = detect_ats_hacks("Normal resume", raw_markup=markup)
    assert result["is_flagged"] is True
    assert any(t["type"] == "micro_font_hidden" for t in result["detected_traps"])
    assert result["clean_text_certified"] is False


def test_offscreen_hidden_element():
    markup = "<div style='position: absolute; left: -9999px; display: none;'>AWS GCP Azure</div>"
    result = detect_ats_hacks("Normal resume text", raw_markup=markup)
    assert result["is_flagged"] is True
    assert any(t["type"] == "offscreen_hidden_element" for t in result["detected_traps"])


def test_invisible_unicode_injection():
    # 20 zero-width spaces injected
    invisible_text = "Experienced" + ("\u200B" * 20) + "Software Developer"
    result = detect_ats_hacks(invisible_text)
    assert result["is_flagged"] is True
    assert any(t["type"] == "invisible_unicode_injection" for t in result["detected_traps"])


def test_consecutive_keyword_stuffing():
    spam_text = "Skills: Python python Python python python python java"
    result = detect_ats_hacks(spam_text)
    assert result["is_flagged"] is True
    assert any(t["type"] == "consecutive_keyword_stuffing" for t in result["detected_traps"])


def test_unpunctuated_keyword_dump():
    dump_text = "skills: python, java, c++, ruby, rust, golang, typescript, javascript, html, css, react, angular, vue, docker, kubernetes, aws, gcp, azure, kafka, redis"
    result = detect_ats_hacks(dump_text)
    assert result["is_flagged"] is True
    assert any(t["type"] == "unpunctuated_keyword_dump" for t in result["detected_traps"])


def test_word_joiner_and_bom_unicode_injection():
    # Word joiner (\u2060) and Zero Width Non-Breaking Space (\uFEFF)
    injected = "Engineer" + ("\u2060\uFEFF" * 8) + "Architect"
    result = detect_ats_hacks(injected)
    assert result["is_flagged"] is True
    assert any(t["type"] == "invisible_unicode_injection" for t in result["detected_traps"])


def test_rgba_zero_opacity_color():
    markup = "<p style='color: rgba(255, 255, 255, 0);'>Hidden React Node GraphQL</p>"
    result = detect_ats_hacks("Standard text", raw_markup=markup)
    assert result["is_flagged"] is True
    assert any(t["type"] == "white_font_stuffing" for t in result["detected_traps"])


def test_empty_input():
    result = detect_ats_hacks("", raw_markup="")
    assert result["hack_risk_score"] == 100
    assert result["clean_text_certified"] is True

