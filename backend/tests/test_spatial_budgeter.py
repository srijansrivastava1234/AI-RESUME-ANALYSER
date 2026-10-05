import pytest
from backend.app.spatial_budgeter import audit_canvas_spatial_budget, BoundingBox

def test_empty_canvas_budget():
    res = audit_canvas_spatial_budget([])
    assert res["status"] == "EMPTY"
    assert res["is_valid_layout"] is True
    assert res["page_count"] == 0

def test_valid_single_column_layout():
    boxes = [
        {"id": "header", "x": 36.0, "y": 36.0, "width": 540.0, "height": 60.0, "page": 1},
        {"id": "summary", "x": 36.0, "y": 105.0, "width": 540.0, "height": 50.0, "page": 1},
        {"id": "experience_1", "x": 36.0, "y": 165.0, "width": 540.0, "height": 180.0, "page": 1},
        {"id": "experience_2", "x": 36.0, "y": 355.0, "width": 540.0, "height": 180.0, "page": 1},
        {"id": "education", "x": 36.0, "y": 545.0, "width": 540.0, "height": 80.0, "page": 1},
        {"id": "skills", "x": 36.0, "y": 635.0, "width": 540.0, "height": 90.0, "page": 1}
    ]
    res = audit_canvas_spatial_budget(boxes, page_format="letter", min_margin_pt=36.0)
    assert res["status"] == "VALID"
    assert res["is_valid_layout"] is True
    assert res["collision_count"] == 0
    assert res["margin_violation_count"] == 0
    assert 0.45 <= res["density_ratio"] <= 0.80

def test_margin_overflow_and_bounding_collision():
    boxes = [
        # Box breaching left and top margins
        {"id": "bad_header", "x": 10.0, "y": 20.0, "width": 540.0, "height": 50.0, "page": 1},
        # Box overlapping bad_header
        {"id": "colliding_block", "x": 50.0, "y": 40.0, "width": 300.0, "height": 60.0, "page": 1},
        # Box with narrow horizontal gutter (<12pt)
        {"id": "left_col", "x": 36.0, "y": 200.0, "width": 200.0, "height": 100.0, "page": 1},
        {"id": "right_col", "x": 242.0, "y": 200.0, "width": 200.0, "height": 100.0, "page": 1} # gutter = 6pt
    ]
    res = audit_canvas_spatial_budget(boxes, page_format="letter", min_margin_pt=36.0)
    assert res["status"] == "INVALID"
    assert res["is_valid_layout"] is False
    assert res["collision_count"] >= 1
    assert res["margin_violation_count"] >= 1
    assert res["gutter_warning_count"] >= 1
    assert any("bad_header" in m["element_id"] for m in res["margin_violations"])
