import io
import re
import logging
from typing import List, Dict, Any, Optional
from pypdf import PdfReader

logger = logging.getLogger("PDFLayoutExtractor")

SECTION_HEADER_PATTERNS = [
    r'^(?:work\s+)?experience\b',
    r'^employment(?:\s+history)?\b',
    r'^professional\s+experience\b',
    r'^education\b',
    r'^academic\s+(?:background|history)\b',
    r'^skills\b',
    r'^technical\s+skills\b',
    r'^core\s+competencies\b',
    r'^projects\b',
    r'^certifications?\b',
    r'^awards?\b',
    r'^summary\b',
    r'^professional\s+summary\b',
    r'^profile\b',
    r'^publications?\b',
    r'^languages?\b'
]

CONTACT_PATTERNS = [
    r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',  # Email
    r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone
    r'linkedin\.com/in/[a-zA-Z0-9_-]+',  # LinkedIn
    r'github\.com/[a-zA-Z0-9_-]+',  # GitHub
    r'https?://[^\s]+'  # URL
]

METRIC_PATTERNS = [
    r'\b\d+(?:\.\d+)?%',
    r'\$\s*\d+(?:,\d{3})*(?:\.\d+)?[kKmMbB]?',
    r'\b\d+(?:,\d{3})+\b',
    r'\b\d+\s*(?:ms|sec|hours?|days?|users?|clients?|engineers?|team\s+members?|x|X)\b'
]

def clamp_viewport_bounds(val: float, min_bound: float = 0.0, max_bound: float = 1.0) -> float:
    """Clamps a floating coordinate strictly between min_bound and max_bound."""
    return max(min_bound, min(max_bound, float(val)))


def normalize_bbox_coordinates(
    x_pt: float,
    y_pt: float,
    width_pt: float,
    height_pt: float,
    page_width: float,
    page_height: float
) -> Dict[str, float]:
    """
    Converts absolute PDF point dimensions to normalized (0.0 - 1.0) viewport coordinates
    with strictly enforced boundary safety and sub-millimeter precision.
    """
    safe_pw = max(1.0, page_width)
    safe_ph = max(1.0, page_height)
    x_norm = clamp_viewport_bounds(x_pt / safe_pw)
    y_norm = clamp_viewport_bounds(y_pt / safe_ph)
    w_norm = clamp_viewport_bounds(width_pt / safe_pw, min_bound=0.01)
    h_norm = clamp_viewport_bounds(height_pt / safe_ph, min_bound=0.01)
    return {
        "x": round(x_norm, 4),
        "y": round(y_norm, 4),
        "w": round(w_norm, 4),
        "h": round(h_norm, 4)
    }


def classify_token_type(text: str, y_norm: float, font_size: float, avg_font_size: float) -> str:
    """
    Classifies a text block into a semantic ATS role:
    - 'header': Section title or Candidate Name
    - 'contact': Email, phone, portfolio links in upper viewport
    - 'bullet': Action-oriented bullet point
    - 'body': General descriptor or dates
    """
    cleaned = text.strip()
    if not cleaned:
        return "body"

    # Check for Contact in top 25% of the page
    if y_norm <= 0.25:
        for pat in CONTACT_PATTERNS:
            if re.search(pat, cleaned, re.IGNORECASE):
                return "contact"

    # Check for Name/Header: Top 15% with large font size
    if y_norm <= 0.15 and font_size >= avg_font_size * 1.25 and len(cleaned.split()) <= 4:
        return "header"

    # Check for Section Header
    clean_lower = cleaned.lower()
    for pat in SECTION_HEADER_PATTERNS:
        if re.search(pat, clean_lower) and len(cleaned.split()) <= 4:
            return "header"

    # Check for bullet point
    if cleaned.startswith(('•', '-', '–', '—', '*', '▪', '►', '✓')) or re.match(r'^\d+\.\s', cleaned):
        return "bullet"

    # If font size is noticeably larger than average and short line -> likely a header/subhead
    if font_size >= avg_font_size * 1.2 and len(cleaned.split()) <= 6:
        return "header"

    return "body"


def calculate_gaze_weight(token_type: str, y_norm: float, x_norm: float, text: str, font_size: float, avg_font_size: float) -> float:
    """
    Calculates the recruiter eye-tracking gaze intensity (0.0 to 1.0)
    simulating the classic 6-second F-pattern / Z-pattern eye gaze.

    Recruiters fixate heavily on:
    1. Top header / candidate identity (Y <= 15%)
    2. Left-hand margin (X <= 35%)
    3. Section titles and job titles
    4. First 2 bullet points under current job
    5. Quantified impact metrics ($/%, numbers)
    """
    # Base weight by vertical position (F-pattern top bias)
    if y_norm <= 0.15:
        pos_weight = 0.95
    elif y_norm <= 0.35:
        pos_weight = 0.80
    elif y_norm <= 0.60:
        pos_weight = 0.55
    else:
        pos_weight = 0.30

    # Horizontal position bias (left-to-right reading scan)
    if x_norm <= 0.35:
        x_mult = 1.15
    elif x_norm <= 0.70:
        x_mult = 1.0
    else:
        x_mult = 0.85

    # Type multiplier
    type_mult = 1.0
    if token_type == "header":
        type_mult = 1.3
    elif token_type == "contact":
        type_mult = 1.1
    elif token_type == "bullet":
        type_mult = 1.05

    # Metric boost
    metric_boost = 0.0
    for pat in METRIC_PATTERNS:
        if re.search(pat, text):
            metric_boost = 0.20
            break

    # Font size relative boost
    size_boost = 0.1 if font_size > avg_font_size else 0.0

    raw_score = (pos_weight * x_mult * type_mult) + metric_boost + size_boost
    return round(min(1.0, max(0.05, raw_score)), 2)


def extract_pdf_layout_tokens(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts high-fidelity layout tokens, normalized bounding boxes,
    and simulated recruiter gaze weights from a PDF document.
    """
    if not pdf_bytes:
        return {
            "success": False,
            "error": "Empty PDF byte stream provided",
            "page_count": 0,
            "pages": []
        }

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        if page_count == 0:
            return {
                "success": False,
                "error": "PDF has 0 pages",
                "page_count": 0,
                "pages": []
            }

        pages_data = []

        for page_idx, page in enumerate(reader.pages):
            media_box = page.mediabox
            page_width = float(media_box.width) if media_box.width else 612.0
            page_height = float(media_box.height) if media_box.height else 792.0

            raw_spans = []

            def visitor_body(text, cm, tm, font_dict, font_size):
                stripped = text.strip()
                if not stripped:
                    return

                # In PDF coordinate system, origin (0,0) is bottom-left.
                # tm[4] is X coordinate, tm[5] is Y coordinate from bottom.
                x_pt = float(tm[4]) if len(tm) > 4 else 0.0
                y_bottom_pt = float(tm[5]) if len(tm) > 5 else 0.0
                
                # Convert to top-left origin
                y_top_pt = page_height - y_bottom_pt
                f_size = float(font_size) if font_size else 11.0

                raw_spans.append({
                    "text": stripped,
                    "x_pt": x_pt,
                    "y_pt": y_top_pt,
                    "font_size": f_size,
                    "font_name": font_dict.get("/BaseFont", "Unknown") if isinstance(font_dict, dict) else "Unknown"
                })

            try:
                page.extract_text(visitor_text=visitor_body)
            except Exception as visitor_err:
                logger.warning(f"Visitor text extraction failed for page {page_idx + 1}: {visitor_err}")

            # If visitor extraction found nothing (e.g. non-standard stream), fallback to standard line splitting
            if not raw_spans:
                plain_text = page.extract_text() or ""
                lines = [l.strip() for l in plain_text.splitlines() if l.strip()]
                line_height = page_height / max(len(lines) + 1, 20)
                for idx, line in enumerate(lines):
                    raw_spans.append({
                        "text": line,
                        "x_pt": 54.0,  # 0.75 inch margin
                        "y_pt": (idx + 1) * line_height,
                        "font_size": 11.0,
                        "font_name": "Standard"
                    })

            # Calculate average font size
            font_sizes = [s["font_size"] for s in raw_spans if s["font_size"] > 0]
            avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 11.0

            # Group spans into lines / blocks if they share similar Y coordinates (+- 4pt)
            raw_spans.sort(key=lambda s: (round(s["y_pt"] / 4.0), s["x_pt"]))

            grouped_lines = []
            curr_line = None

            for span in raw_spans:
                if curr_line is None:
                    curr_line = {
                        "text": span["text"],
                        "min_x": span["x_pt"],
                        "max_x": span["x_pt"] + (len(span["text"]) * span["font_size"] * 0.5),
                        "y_pt": span["y_pt"],
                        "font_size": span["font_size"],
                        "font_name": span["font_name"]
                    }
                else:
                    if abs(span["y_pt"] - curr_line["y_pt"]) <= 5.0 and abs(span["x_pt"] - curr_line["max_x"]) <= 40.0:
                        curr_line["text"] += " " + span["text"]
                        curr_line["max_x"] = max(curr_line["max_x"], span["x_pt"] + (len(span["text"]) * span["font_size"] * 0.5))
                        curr_line["font_size"] = max(curr_line["font_size"], span["font_size"])
                    else:
                        grouped_lines.append(curr_line)
                        curr_line = {
                            "text": span["text"],
                            "min_x": span["x_pt"],
                            "max_x": span["x_pt"] + (len(span["text"]) * span["font_size"] * 0.5),
                            "y_pt": span["y_pt"],
                            "font_size": span["font_size"],
                            "font_name": span["font_name"]
                        }
            if curr_line:
                grouped_lines.append(curr_line)

            tokens = []
            for order_idx, line in enumerate(grouped_lines):
                bbox = normalize_bbox_coordinates(
                    x_pt=line["min_x"],
                    y_pt=line["y_pt"] - line["font_size"],
                    width_pt=line["max_x"] - line["min_x"],
                    height_pt=line["font_size"] * 1.3,
                    page_width=page_width,
                    page_height=page_height
                )

                t_type = classify_token_type(line["text"], bbox["y"], line["font_size"], avg_font_size)
                gaze_weight = calculate_gaze_weight(t_type, bbox["y"], bbox["x"], line["text"], line["font_size"], avg_font_size)

                tokens.append({
                    "reading_order": order_idx + 1,
                    "text": line["text"],
                    "type": t_type,
                    "font_size": round(line["font_size"], 1),
                    "gaze_weight": gaze_weight,
                    "bbox": bbox
                })


            pages_data.append({
                "page_number": page_idx + 1,
                "width_pt": page_width,
                "height_pt": page_height,
                "token_count": len(tokens),
                "tokens": tokens
            })

        return {
            "success": True,
            "page_count": page_count,
            "pages": pages_data,
            "summary": {
                "total_tokens": sum(p["token_count"] for p in pages_data),
                "avg_gaze_density": round(
                    sum(t["gaze_weight"] for p in pages_data for t in p["tokens"]) / 
                    max(1, sum(p["token_count"] for p in pages_data)), 2
                )
            }
        }
    except Exception as e:
        logger.error(f"Error extracting PDF layout tokens: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "page_count": 0,
            "pages": []
        }
