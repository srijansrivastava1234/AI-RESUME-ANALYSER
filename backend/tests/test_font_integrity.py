import pytest
from app.font_integrity import normalize_typographic_ligatures, audit_font_cmap_integrity

def test_empty_and_whitespace_input():
    empty_norm, counts, words = normalize_typographic_ligatures("")
    assert empty_norm == ""
    assert counts == {}
    assert words == []

    audit = audit_font_cmap_integrity("")
    assert audit["font_health_score"] == 0
    assert not audit["iso_19005_compliant"]
    assert not audit["is_searchable"]

    audit_ws = audit_font_cmap_integrity("    \n\t   ")
    assert audit_ws["font_health_score"] == 0
    assert not audit_ws["iso_19005_compliant"]

def test_clean_text_layer_iso_compliant():
    clean_text = (
        "Jane Doe\n"
        "Lead DevOps Engineer with 8 years of experience in AWS, Kubernetes, Terraform, and Docker.\n"
        "Architected scalable infrastructure reducing deployment downtime by 40%."
    )
    audit = audit_font_cmap_integrity(clean_text)
    assert audit["font_health_score"] == 100
    assert audit["iso_19005_compliant"] is True
    assert audit["is_searchable"] is True
    assert audit["pua_glyph_count"] == 0
    assert audit["replacement_char_count"] == 0
    assert audit["soft_hyphen_count"] == 0
    assert audit["ligature_count"] == 0
    assert "ISO 19005-2 PDF/A text layer compliance verified" in audit["remediations"][0]

def test_typographic_ligature_normalization():
    # Text with \uFB01 (fi), \uFB02 (fl), \uFB03 (ffi), \u0153 (oe)
    ligature_text = (
        "Architected an e\uFB03cient work\uFB02ow to de\uFB01ne c\u0153fficient data pipelines."
    )
    norm_text, counts, words = normalize_typographic_ligatures(ligature_text)
    assert "efficient" in norm_text
    assert "workflow" in norm_text
    assert "define" in norm_text
    assert "coefficient" in norm_text
    assert counts["ffi"] == 1
    assert counts["fl"] == 1
    assert counts["fi"] == 1
    assert counts["oe"] == 1
    assert len(words) >= 3
    assert any("➔ 'efficient'" in w for w in words)

    # Check audit reflects ligature decomposition
    audit = audit_font_cmap_integrity(ligature_text + " Extra padding words for searchability test.")
    assert audit["ligature_count"] == 4
    assert len(audit["recovered_words"]) >= 3
    assert any("typographic ligature" in rem for rem in audit["remediations"])

def test_pua_glyph_detection():
    # \uE001 is a Private Use Area icon glyph often emitted by FontAwesome without /ToUnicode CMap
    pua_text = "Phone: \uE001 555-123-4567 | Email: \uE002 jane@example.com | Skills: Python, AWS"
    audit = audit_font_cmap_integrity(pua_text)
    assert audit["pua_glyph_count"] == 2
    assert audit["font_health_score"] <= 90
    assert audit["iso_19005_compliant"] is False
    assert any("Private Use Area (PUA) glyph" in rem for rem in audit["remediations"])

def test_replacement_char_corruption():
    # \uFFFD indicates font decoding failure
    corrupt_text = "Senior \uFFFD Software \uFFFD Engineer at Enterprise Cloud Corp."
    audit = audit_font_cmap_integrity(corrupt_text)
    assert audit["replacement_char_count"] == 2
    assert audit["font_health_score"] <= 90
    assert audit["iso_19005_compliant"] is False
    assert any("Unicode replacement character" in rem for rem in audit["remediations"])

def test_soft_hyphen_decontamination():
    # \u00AD is soft hyphen
    hyphenated_text = "Implemented Micro\u00ADservices and Cloud\u00ADnative container orchestrations on AWS."
    audit = audit_font_cmap_integrity(hyphenated_text)
    assert audit["soft_hyphen_count"] == 2
    assert audit["iso_19005_compliant"] is False
    assert any("soft hyphen" in rem for rem in audit["remediations"])

def test_zero_width_character_penalty():
    # \u200B is zero width space
    hidden_text = "Normal Text" + ("\u200B" * 8) + " with hidden zero-width spaces."
    audit = audit_font_cmap_integrity(hidden_text)
    assert audit["zero_width_count"] == 8
    assert audit["font_health_score"] <= 85
    assert any("zero-width or invisible characters" in rem for rem in audit["remediations"])

def test_unsearchable_low_score():
    corrupt_unsearchable = "\uFFFD" * 15
    audit = audit_font_cmap_integrity(corrupt_unsearchable)
    assert audit["font_health_score"] <= 60
    assert audit["is_searchable"] is False
