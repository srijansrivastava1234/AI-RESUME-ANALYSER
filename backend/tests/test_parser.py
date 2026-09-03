import pytest
from app.parser import extract_text_from_txt, extract_text_from_docx, extract_text_from_pdf

def test_extract_text_from_txt():
    content = b"Software Engineer with 5+ years of experience in Python, FastAPI, and React."
    text = extract_text_from_txt(content)
    assert "Software Engineer" in text
    assert "FastAPI" in text

def test_extract_text_from_txt_empty():
    content = b""
    text = extract_text_from_txt(content)
    assert text == ""

def test_extract_text_from_txt_utf8():
    content = "Senior Developer \u2014 Full Stack \u2022 Cloud Architecture".encode("utf-8")
    text = extract_text_from_txt(content)
    assert "Senior Developer" in text
