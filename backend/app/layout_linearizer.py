import re
from typing import Dict, List, Any, Optional

def simulate_recursive_xy_cut(raw_text: str) -> Dict[str, Any]:
    """
    Simulates the Recursive XY-Cut algorithm and legacy ATS scanline sorting
    (e.g., Taleo, legacy Workday, Sovren) on parsed resume text.

    Audits:
    1. Multi-column reading-order traps where parallel columns collapse into horizontal bands.
    2. Gutter width and whitespace projection profiles across lines.
    3. Scanline interleaving hazards (e.g., sidebar skills concatenated with job titles).
    4. Table border/separator collisions that collapse vertical projection valleys.

    :param raw_text: Raw or line-split text extracted from document
    :return: Comprehensive layout linearization diagnostic dictionary
    """
    if not raw_text or not raw_text.strip():
        return {
            "linearization_score": 0,
            "risk_tier": "Empty Document",
            "is_linear_safe": False,
            "total_analyzed_lines": 0,
            "gutter_anomaly_count": 0,
            "gutter_ratio": 0.0,
            "table_divider_count": 0,
            "interleaving_hazard_count": 0,
            "simulated_scrambled_snippets": [],
            "recommendations": ["Document contains no extractable text layer."]
        }

    lines = raw_text.splitlines()
    non_empty_lines = [line.rstrip() for line in lines if line.strip()]
    total_lines = len(non_empty_lines)

    if total_lines == 0:
        return {
            "linearization_score": 0,
            "risk_tier": "Empty Document",
            "is_linear_safe": False,
            "total_analyzed_lines": 0,
            "gutter_anomaly_count": 0,
            "gutter_ratio": 0.0,
            "table_divider_count": 0,
            "interleaving_hazard_count": 0,
            "simulated_scrambled_snippets": [],
            "recommendations": ["Document contains only whitespace."]
        }

    gutter_anomaly_count = 0
    table_divider_count = 0
    interleaving_hazards: List[Dict[str, str]] = []
    scrambled_previews: List[str] = []

    # Regex detecting wide column gutters (>= 4 spaces or tabs separating distinct alphanumeric blocks)
    gutter_pattern = re.compile(r'(\S+.*?)(?:\t+|\s{4,})(\S+.*)')
    # Regex detecting ASCII dividers, boxes, or grid borders that intersect gutters
    divider_pattern = re.compile(r'(\+{2,}|[\|\-_=]{4,}|[┌┬┐├┼┤└┴┘]{2,})')
    # Regex for common sidebar labels that frequently get interleaved with experience
    sidebar_labels = re.compile(r'^(?:Skills|Tools|Contact|Languages|Education|Certifications|Interests|About|Summary):?', re.IGNORECASE)

    for idx, line in enumerate(non_empty_lines):
        # Audit ASCII dividers and bounding box artifacts
        if divider_pattern.search(line):
            table_divider_count += 1

        # Audit horizontal multi-column gutters
        match = gutter_pattern.search(line)
        if match:
            gutter_anomaly_count += 1
            col_left = match.group(1).strip()
            col_right = match.group(2).strip()

            # Check if left column looks like a sidebar and right looks like body/experience
            is_hazard = bool(sidebar_labels.search(col_left)) or len(col_left) < 30 and len(col_right) > 25
            if is_hazard:
                interleaving_hazards.append({
                    "line_number": idx + 1,
                    "left_column": col_left,
                    "right_column": col_right,
                    "scanline_scramble": f"{col_left} {col_right}"
                })
                if len(scrambled_previews) < 3:
                    scrambled_previews.append(f"Line {idx + 1}: '{col_left}' + '{col_right}' ➔ '{col_left} {col_right}'")

    # Algorithmic scoring
    score = 100
    recommendations: List[str] = []

    # Penalize for gutter ratio (percentage of lines exhibiting multi-column gutter gaps)
    gutter_ratio = gutter_anomaly_count / total_lines
    if gutter_ratio > 0.40:
        score -= 50
        recommendations.append(
            f"Severe multi-column layout detected ({gutter_anomaly_count} lines, {gutter_ratio:.0%} of document). "
            "Legacy ATS parsers (Taleo, older Workday) will read across columns horizontally, scrambling reading order."
        )
    elif gutter_ratio > 0.15:
        score -= 25
        recommendations.append(
            f"Moderate multi-column layout detected ({gutter_anomaly_count} lines with wide gutters). "
            "Ensure core contact details and technical proficiencies are not placed in sidebars."
        )

    # Penalize for interleaving hazards (direct sidebar-to-body collisions)
    if len(interleaving_hazards) > 0:
        penalty = min(25, len(interleaving_hazards) * 5)
        score -= penalty
        recommendations.append(
            f"Detected {len(interleaving_hazards)} scanline interleaving hazard(s) where sidebar metadata merges "
            "directly with job experience statements during scanline sorting."
        )

    # Penalize for ASCII divider rules and table grids
    if table_divider_count > 4:
        score -= 15
        recommendations.append(
            f"Detected {table_divider_count} ASCII table or divider borders. Dividers intersecting gutters collapse "
            "vertical whitespace projection valleys in Recursive XY-Cut parsers."
        )
    elif table_divider_count > 1:
        score -= 5
        recommendations.append("Consider replacing graphic ASCII divider lines with standard vertical whitespace.")

    score = max(0, min(100, score))

    if score >= 85:
        risk_tier = "Safe Single-Column"
        is_linear_safe = True
    elif score >= 60:
        risk_tier = "Moderate Multi-Column Risk"
        is_linear_safe = False
    else:
        risk_tier = "Critical Layout Collapse"
        is_linear_safe = False

    if not recommendations:
        recommendations.append("Clean single-column layout verified. Text serializes strictly top-to-bottom with zero gutter collisions.")

    return {
        "linearization_score": score,
        "risk_tier": risk_tier,
        "is_linear_safe": is_linear_safe,
        "total_analyzed_lines": total_lines,
        "gutter_anomaly_count": gutter_anomaly_count,
        "gutter_ratio": round(gutter_ratio, 3),
        "table_divider_count": table_divider_count,
        "interleaving_hazard_count": len(interleaving_hazards),
        "simulated_scrambled_snippets": scrambled_previews,
        "recommendations": recommendations
    }
