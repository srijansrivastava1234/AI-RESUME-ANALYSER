"""Euclidean Spatial Density & Visual Bounding Box Collision Budgeter.

Models 2D Euclidean spatial geometry for PDF/Canvas resume layouts:
1. Standard page formats (US-Letter: 612x792 pt, A4: 595x842 pt).
2. Safe printable margin violation checks (minimum 36pt / 0.5in margins).
3. Bounding box collision and vertical overlap detection between text elements.
4. Canvas Fill & Visual Reading Density Index (target 45% - 70% fill ratio).
5. Multi-page spillover / orphan element diagnostics.
"""

from typing import Any, Dict, List, Optional, Tuple


class BoundingBox:
    def __init__(self, element_id: str, x: float, y: float, width: float, height: float, page: int = 1):
        self.element_id = element_id
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.page = int(page)

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    def intersects(self, other: "BoundingBox") -> bool:
        if self.page != other.page:
            return False
        return not (
            self.right <= other.x or
            self.x >= other.right or
            self.bottom <= other.y or
            self.y >= other.bottom
        )

    def horizontal_gutter(self, other: "BoundingBox") -> float:
        """Returns distance between horizontal borders if side-by-side on same page."""
        if self.page != other.page:
            return float("inf")
        if self.intersects(other):
            return 0.0
        if self.right <= other.x:
            return other.x - self.right
        if other.right <= self.x:
            return self.x - other.right
        return 0.0


def audit_canvas_spatial_budget(
    boxes: List[Dict[str, Any]],
    page_format: str = "letter",
    min_margin_pt: float = 36.0
) -> Dict[str, Any]:
    """
    Audits a list of Euclidean bounding boxes representing resume elements.
    
    :param boxes: List of dicts with {"id": str, "x": float, "y": float, "width": float, "height": float, "page": int}
    :param page_format: "letter" (612x792 pt) or "a4" (595x842 pt)
    :param min_margin_pt: Minimum allowed margin in points (default 36pt = 0.5 in)
    """
    page_dims = {
        "letter": (612.0, 792.0),
        "a4": (595.0, 842.0)
    }
    canvas_w, canvas_h = page_dims.get(page_format.lower(), (612.0, 792.0))
    canvas_area_per_page = canvas_w * canvas_h

    if not boxes:
        return {
            "status": "EMPTY",
            "is_valid_layout": True,
            "page_count": 0,
            "density_ratio": 0.0,
            "collisions": [],
            "margin_violations": [],
            "gutter_warnings": []
        }

    parsed_boxes: List[BoundingBox] = []
    for b in boxes:
        parsed_boxes.append(BoundingBox(
            element_id=b.get("id", "elem"),
            x=b.get("x", 0.0),
            y=b.get("y", 0.0),
            width=b.get("width", 0.0),
            height=b.get("height", 0.0),
            page=b.get("page", 1)
        ))

    pages_used = max(b.page for b in parsed_boxes)
    total_canvas_area = canvas_area_per_page * pages_used
    total_content_area = sum(b.area for b in parsed_boxes)
    density_ratio = round((total_content_area / total_canvas_area), 4) if total_canvas_area > 0 else 0.0

    margin_violations: List[Dict[str, Any]] = []
    collisions: List[Dict[str, Any]] = []
    gutter_warnings: List[Dict[str, Any]] = []

    # Check margin boundaries
    for box in parsed_boxes:
        reasons = []
        if box.x < min_margin_pt:
            reasons.append(f"Left margin breach ({box.x:.1f}pt < {min_margin_pt}pt)")
        if box.y < min_margin_pt:
            reasons.append(f"Top margin breach ({box.y:.1f}pt < {min_margin_pt}pt)")
        if box.right > (canvas_w - min_margin_pt):
            reasons.append(f"Right margin overflow ({box.right:.1f}pt > {canvas_w - min_margin_pt:.1f}pt)")
        if box.bottom > (canvas_h - min_margin_pt):
            reasons.append(f"Bottom margin overflow ({box.bottom:.1f}pt > {canvas_h - min_margin_pt:.1f}pt)")

        if reasons:
            margin_violations.append({
                "element_id": box.element_id,
                "page": box.page,
                "violations": reasons
            })

    # Pairwise collision & gutter audit
    for i in range(len(parsed_boxes)):
        for j in range(i + 1, len(parsed_boxes)):
            b1 = parsed_boxes[i]
            b2 = parsed_boxes[j]
            if b1.page != b2.page:
                continue

            if b1.intersects(b2):
                collisions.append({
                    "element_1": b1.element_id,
                    "element_2": b2.element_id,
                    "page": b1.page,
                    "overlap_description": f"Direct Euclidean bounding box intersection on Page {b1.page}"
                })
            else:
                # Check horizontal gutter if they share vertical span
                shares_vertical_span = not (b1.bottom <= b2.y or b2.bottom <= b1.y)
                if shares_vertical_span:
                    gutter = b1.horizontal_gutter(b2)
                    if 0 < gutter < 12.0:  # Gutter collapse threshold (< 12pt)
                        gutter_warnings.append({
                            "element_1": b1.element_id,
                            "element_2": b2.element_id,
                            "gutter_pt": round(gutter, 2),
                            "page": b1.page,
                            "hazard": "Gutter collapse (< 12pt) risks column fusion during OCR/linearization."
                        })

    is_valid = len(margin_violations) == 0 and len(collisions) == 0

    return {
        "status": "VALID" if is_valid else "INVALID",
        "is_valid_layout": is_valid,
        "page_count": pages_used,
        "canvas_format": page_format.upper(),
        "density_ratio": density_ratio,
        "density_rating": "Optimal (45-70%)" if 0.45 <= density_ratio <= 0.70 else ("Too Sparse (<45%)" if density_ratio < 0.45 else "Overcrowded (>70%)"),
        "total_elements": len(parsed_boxes),
        "collision_count": len(collisions),
        "collisions": collisions,
        "margin_violation_count": len(margin_violations),
        "margin_violations": margin_violations,
        "gutter_warning_count": len(gutter_warnings),
        "gutter_warnings": gutter_warnings
    }
