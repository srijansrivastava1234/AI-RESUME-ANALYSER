import io
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.pdf_layout import (
    classify_token_type,
    calculate_gaze_weight,
    extract_pdf_layout_tokens
)

client = TestClient(app)
SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sample_resume.pdf")

def test_classify_token_type():
    # Contact in upper section
    assert classify_token_type("alex@example.com | +1 555-0199", y_norm=0.1, font_size=10.0, avg_font_size=11.0) == "contact"
    assert classify_token_type("linkedin.com/in/alex-dev", y_norm=0.15, font_size=10.0, avg_font_size=11.0) == "contact"

    # Header in upper section
    assert classify_token_type("Alex Johnson", y_norm=0.08, font_size=18.0, avg_font_size=11.0) == "header"
    assert classify_token_type("WORK EXPERIENCE", y_norm=0.3, font_size=14.0, avg_font_size=11.0) == "header"
    assert classify_token_type("Technical Skills", y_norm=0.7, font_size=13.0, avg_font_size=11.0) == "header"

    # Bullet point
    assert classify_token_type("• Architected distributed pipeline improving latency by 45%", y_norm=0.4, font_size=11.0, avg_font_size=11.0) == "bullet"
    assert classify_token_type("- Developed REST API with FastAPI", y_norm=0.5, font_size=11.0, avg_font_size=11.0) == "bullet"

    # General body
    assert classify_token_type("San Francisco, CA | May 2021 - Present", y_norm=0.45, font_size=10.0, avg_font_size=11.0) == "body"
    assert classify_token_type("", y_norm=0.5, font_size=11.0, avg_font_size=11.0) == "body"


def test_calculate_gaze_weight():
    # Top header should have highest gaze attention
    w_top = calculate_gaze_weight("header", y_norm=0.05, x_norm=0.1, text="Jane Doe", font_size=18.0, avg_font_size=11.0)
    assert w_top >= 0.85

    # Lower body without metrics should have moderate/lower attention
    w_low = calculate_gaze_weight("body", y_norm=0.85, x_norm=0.8, text="References available upon request", font_size=10.0, avg_font_size=11.0)
    assert w_low < w_top

    # Bullet with quantified metric receives a boost
    w_metric = calculate_gaze_weight("bullet", y_norm=0.3, x_norm=0.15, text="Boosted revenue by $2.5M and 35%", font_size=11.0, avg_font_size=11.0)
    w_no_metric = calculate_gaze_weight("bullet", y_norm=0.3, x_norm=0.15, text="Responsible for system operations", font_size=11.0, avg_font_size=11.0)
    assert w_metric > w_no_metric


def test_extract_pdf_layout_tokens_empty_or_invalid():
    res_empty = extract_pdf_layout_tokens(b"")
    assert res_empty["success"] is False
    assert res_empty["page_count"] == 0

    res_invalid = extract_pdf_layout_tokens(b"not a valid pdf content")
    assert res_invalid["success"] is False


def test_extract_pdf_layout_tokens_sample_pdf():
    if not os.path.exists(SAMPLE_PDF_PATH):
        pytest.skip("sample_resume.pdf not found in root")

    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    res = extract_pdf_layout_tokens(pdf_bytes)
    assert res["success"] is True
    assert res["page_count"] >= 1
    assert len(res["pages"]) >= 1

    first_page = res["pages"][0]
    assert first_page["width_pt"] > 0
    assert first_page["height_pt"] > 0
    assert first_page["token_count"] > 0

    # Ensure tokens have valid normalized bbox coordinates [0, 1]
    for token in first_page["tokens"]:
        assert 0.0 <= token["bbox"]["x"] <= 1.0
        assert 0.0 <= token["bbox"]["y"] <= 1.0
        assert token["bbox"]["w"] > 0.0
        assert token["bbox"]["h"] > 0.0
        assert 0.0 <= token["gaze_weight"] <= 1.0
        assert token["type"] in ["header", "contact", "bullet", "body"]


def test_pdf_layout_tokens_api_endpoint():
    if not os.path.exists(SAMPLE_PDF_PATH):
        pytest.skip("sample_resume.pdf not found in root")

    with open(SAMPLE_PDF_PATH, "rb") as f:
        response = client.post(
            "/api/pdf-layout-tokens",
            files={"file": ("sample_resume.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["page_count"] >= 1
    assert "pages" in data
    assert "summary" in data


def test_pdf_layout_tokens_api_non_pdf():
    response = client.post(
        "/api/pdf-layout-tokens",
        files={"file": ("resume.txt", io.BytesIO(b"Hello world"), "text/plain")}
    )
    assert response.status_code == 400
    assert "only supported for PDF" in response.json()["detail"]
