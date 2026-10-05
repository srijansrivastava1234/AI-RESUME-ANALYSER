import pytest
from backend.app.adversarial_steganography import (
    decode_zero_width_binary_payload,
    detect_homoglyph_substitutions,
    sanitize_adversarial_text,
    ZWSP,
    ZWNJ
)

def test_empty_adversarial_text():
    sanitized, report = sanitize_adversarial_text("")
    assert sanitized == ""
    assert report["is_adversarial"] is False
    assert report["threat_score"] == 0

def test_zero_width_binary_payload_extraction():
    # Encode 'HI' in binary (01001000 01001001)
    # 0 = ZWSP, 1 = ZWNJ
    h_bits = "01001000"
    i_bits = "01001001"
    
    hidden_payload = "".join(ZWNJ if b == '1' else ZWSP for b in (h_bits + i_bits))
    tampered_text = f"Software Engineer{hidden_payload} with 5 years experience."
    
    decoded = decode_zero_width_binary_payload(tampered_text)
    assert "HI" in decoded
    
    sanitized, report = sanitize_adversarial_text(tampered_text)
    assert report["steganography_detected"] is True
    assert "HI" in report["decoded_payloads"]
    assert report["threat_score"] >= 60
    assert ZWSP not in sanitized
    assert ZWNJ not in sanitized

def test_homoglyph_attack_detection():
    # 'Python' where 'o' is Cyrillic small 'о' (\u043e)
    # 'AWS' where 'A' is Cyrillic capital 'А' (\u0410)
    tampered_word_1 = "Pyth\u043en"
    tampered_word_2 = "\u0410WS"
    text = f"Expert in {tampered_word_1} and {tampered_word_2} cloud infrastructure."
    
    homoglyphs = detect_homoglyph_substitutions(text)
    assert len(homoglyphs) == 2
    assert homoglyphs[0]["canonical"] == "Python"
    assert homoglyphs[1]["canonical"] == "AWS"
    
    sanitized, report = sanitize_adversarial_text(text)
    assert report["homoglyphs_detected"] == 2
    assert "Python" in sanitized
    assert "AWS" in sanitized
    assert "\u043e" not in sanitized
    assert "\u0410" not in sanitized
