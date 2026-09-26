import pytest
from app.pdf_layout import (
    clamp_viewport_bounds,
    normalize_bbox_coordinates,
    classify_token_type,
    calculate_gaze_weight,
    extract_pdf_layout_tokens,
)

def test_clamp_viewport_bounds():
    assert clamp_viewport_bounds(-0.5) == 0.0
    assert clamp_viewport_bounds(1.5) == 1.0
    assert clamp_viewport_bounds(0.42) == 0.42
    assert clamp_viewport_bounds(-10.0, min_bound=0.1) == 0.1
    assert clamp_viewport_bounds(10.0, max_bound=0.9) == 0.9

def test_normalize_bbox_coordinates():
    bbox = normalize_bbox_coordinates(
        x_pt=54.0,
        y_pt=100.0,
        width_pt=500.0,
        height_pt=14.0,
        page_width=612.0,
        page_height=792.0
    )
    assert 0.0 <= bbox["x"] <= 1.0
    assert 0.0 <= bbox["y"] <= 1.0
    assert 0.0 < bbox["w"] <= 1.0
    assert 0.0 < bbox["h"] <= 1.0
    assert bbox["x"] == round(54.0 / 612.0, 4)

def test_normalize_bbox_coordinates_zero_dimensions():
    # Defensive guard against 0 page height/width
    bbox = normalize_bbox_coordinates(
        x_pt=10.0,
        y_pt=20.0,
        width_pt=0.0,
        height_pt=0.0,
        page_width=0.0,
        page_height=0.0
    )
    assert bbox["x"] == 1.0
    assert bbox["w"] >= 0.01

def test_classify_token_type_edge_cases():
    # Empty string
    assert classify_token_type("", 0.1, 12.0, 10.0) == "body"
    assert classify_token_type("   ", 0.1, 12.0, 10.0) == "body"

    # Contact in upper page
    assert classify_token_type("john.doe@email.com", 0.05, 10.0, 10.0) == "contact"
    assert classify_token_type("linkedin.com/in/johndoe", 0.10, 10.0, 10.0) == "contact"

    # Header patterns
    assert classify_token_type("WORK EXPERIENCE", 0.30, 12.0, 10.0) == "header"
    assert classify_token_type("Technical Skills", 0.50, 12.0, 10.0) == "header"
    assert classify_token_type("Certifications", 0.70, 12.0, 10.0) == "header"

    # Bullet point symbols
    assert classify_token_type("• Led development of distributed database", 0.40, 10.0, 10.0) == "bullet"
    assert classify_token_type("- Architected backend microservices", 0.40, 10.0, 10.0) == "bullet"
    assert classify_token_type("1. Spearheaded migration to Kubernetes", 0.40, 10.0, 10.0) == "bullet"

def test_calculate_gaze_weight():
    # Top header should have highest gaze weight
    top_header_weight = calculate_gaze_weight("header", 0.05, 0.1, "Senior Cloud Architect", 16.0, 11.0)
    # Bottom body text should have lower gaze weight
    bottom_body_weight = calculate_gaze_weight("body", 0.90, 0.8, "Additional details available on request", 9.0, 11.0)
    
    assert top_header_weight > bottom_body_weight
    assert 0.05 <= top_header_weight <= 1.0
    assert 0.05 <= bottom_body_weight <= 1.0

def test_extract_pdf_layout_tokens_empty_bytes():
    res = extract_pdf_layout_tokens(b"")
    assert res["success"] is False
    assert res["page_count"] == 0
