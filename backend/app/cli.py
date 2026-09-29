"""
Module: cli.py
Purpose: Interactive Command-Line Dashboard, Batch Resume Evaluator,
and Dynamic SVG Badge Generator for automated ATS resume auditing and CI/CD integration.
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any, List

from app.parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from app.analyzer import analyze_resume


# ANSI Color & Formatting Constants (supports Windows 10+ Virtual Terminal & Linux/macOS)
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Background colors
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"
    BG_YELLOW = "\033[43m"
    BG_RED = "\033[41m"
    BG_DARK = "\033[48;5;236m"


def supports_color() -> bool:
    """Check if the current terminal supports ANSI color escape codes."""
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True


USE_COLOR = supports_color()


def colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color code if supported."""
    return f"{color}{text}{Colors.RESET}" if USE_COLOR else text


def get_grade_info(score: int) -> Dict[str, str]:
    """Return grade letter, color, and tier description for a given score."""
    score = max(0, min(100, int(score)))
    if score >= 90:
        return {"grade": "A+", "color": Colors.GREEN, "hex": "#10b981", "desc": "Tier-1 Ready (High ATS Pass)"}
    elif score >= 80:
        return {"grade": "A", "color": Colors.GREEN, "hex": "#10b981", "desc": "Strong Match"}
    elif score >= 70:
        return {"grade": "B", "color": Colors.CYAN, "hex": "#38bdf8", "desc": "Moderate Match"}
    elif score >= 60:
        return {"grade": "C", "color": Colors.YELLOW, "hex": "#f59e0b", "desc": "Parsing / Gap Risks"}
    else:
        return {"grade": "D", "color": Colors.RED, "hex": "#ef4444", "desc": "High Rejection Probability"}


def render_progress_bar(score: int, width: int = 24) -> str:
    """Render a visual terminal progress bar."""
    filled = int(round((score / 100.0) * width))
    empty = width - filled
    grade_info = get_grade_info(score)
    bar = f"{grade_info['color']}{'█' * filled}{Colors.DIM}{'░' * empty}{Colors.RESET}" if USE_COLOR else f"[{'#' * filled}{'.' * empty}]"
    return bar


def generate_svg_badge(ats_score: int, label: str = "ATS Score") -> str:
    """
    Generates a crisp, retina-ready Shields.io-style SVG status badge.
    """
    score = max(0, min(100, int(ats_score)))
    grade_info = get_grade_info(score)
    bg_color = grade_info["hex"]
    grade = grade_info["grade"]

    value_text = f"{score}/100 • {grade}"
    
    # Text width heuristics
    label_width = len(label) * 7 + 14
    value_width = len(value_text) * 7 + 16
    total_width = label_width + value_width
    label_x = label_width / 2
    value_x = label_width + (value_width / 2)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="24" role="img" aria-label="{label}: {value_text}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="24" rx="4" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="24" fill="#1e293b"/>
    <rect x="{label_width}" width="{value_width}" height="24" fill="{bg_color}"/>
    <rect width="{total_width}" height="24" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text aria-hidden="true" x="{label_x}" y="16" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_x}" y="15" fill="#f8fafc">{label}</text>
    <text aria-hidden="true" x="{value_x}" y="16" fill="#010101" fill-opacity=".3">{value_text}</text>
    <text x="{value_x}" y="15" font-weight="bold" fill="#ffffff">{value_text}</text>
  </g>
</svg>"""
    return svg.strip()


def parse_resume_file(file_path: str) -> str:
    """Extracts plain text from a resume file based on extension."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    with open(file_path, 'rb') as f:
        content = f.read()

    if ext == '.pdf':
        return extract_text_from_pdf(content)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(content)
    elif ext in ['.txt', '.md']:
        return extract_text_from_txt(content)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Supported: .pdf, .docx, .txt, .md")


def print_single_resume_dashboard(resume_path: str, report: Dict[str, Any], jd_path: Optional[str] = None):
    """Prints a styled terminal dashboard for a single resume audit."""
    ats_score = report.get('ats_score', 0)
    grade_info = get_grade_info(ats_score)
    bar = render_progress_bar(ats_score, width=28)
    filename = os.path.basename(resume_path)

    print("\n" + colorize("╔" + "═" * 68 + "╗", Colors.CYAN))
    print(colorize("║", Colors.CYAN) + f"   {colorize('AI RESUME ANALYSER', Colors.BOLD + Colors.WHITE)} — {colorize('ATS COMPLIANCE AUDIT DASHBOARD', Colors.CYAN):<53}" + colorize("║", Colors.CYAN))
    print(colorize("╠" + "═" * 68 + "╣", Colors.CYAN))
    
    print(colorize("║", Colors.CYAN) + f"  {colorize('Target File:', Colors.BOLD)} {filename:<54}" + colorize("║", Colors.CYAN))
    if jd_path:
        print(colorize("║", Colors.CYAN) + f"  {colorize('Target Job:', Colors.BOLD)}  {os.path.basename(jd_path):<54}" + colorize("║", Colors.CYAN))
    print(colorize("╟" + "─" * 68 + "╢", Colors.CYAN))

    # Overall Score & Letter Grade Banner
    score_display = f"Overall ATS Score: {colorize(str(ats_score), Colors.BOLD + grade_info['color'])}/100  Grade: {colorize(grade_info['grade'], Colors.BOLD + grade_info['color'])} ({grade_info['desc']})"
    print(colorize("║", Colors.CYAN) + f"  {score_display:<77}" + colorize("║", Colors.CYAN))
    print(colorize("║", Colors.CYAN) + f"  Progress: {bar}  [{ats_score}%]" + " " * (32 - len(str(ats_score))) + colorize("║", Colors.CYAN))
    print(colorize("╠" + "═" * 68 + "╣", Colors.CYAN))

    # Metric Breakdown Table
    print(colorize("║", Colors.CYAN) + f"  {colorize('CORE AUDIT METRICS', Colors.BOLD + Colors.WHITE):<66}" + colorize("║", Colors.CYAN))
    print(colorize("╟" + "─" * 68 + "╢", Colors.CYAN))
    
    metrics = report.get('metrics', [])
    for m in metrics:
        m_name = m.get('name', 'Metric')
        m_score = m.get('score', 0)
        m_grade = get_grade_info(m_score)
        m_bar = render_progress_bar(m_score, width=12)
        print(colorize("║", Colors.CYAN) + f"  • {m_name:<26} {m_bar} {colorize(f'{m_score:3d}/100', m_grade['color'])} [{m_grade['grade']}]   " + colorize("║", Colors.CYAN))
    
    # Key Strengths
    strengths = report.get('key_strengths', [])
    if strengths:
        print(colorize("╟" + "─" * 68 + "╢", Colors.CYAN))
        print(colorize("║", Colors.CYAN) + f"  {colorize('KEY STRENGTHS', Colors.BOLD + Colors.GREEN):<66}" + colorize("║", Colors.CYAN))
        for s in strengths[:4]:
            print(colorize("║", Colors.CYAN) + f"  {colorize('✔', Colors.GREEN)} {s[:62]:<64}" + colorize("║", Colors.CYAN))

    # Missing Keywords & Keyword Gaps
    keywords = report.get('keywords', {})
    missing_kws = keywords.get('missing', [])
    if missing_kws:
        print(colorize("╟" + "─" * 68 + "╢", Colors.CYAN))
        print(colorize("║", Colors.CYAN) + f"  {colorize('TOP MISSING KEYWORDS (ATS GAP)', Colors.BOLD + Colors.YELLOW):<66}" + colorize("║", Colors.CYAN))
        kw_line = ", ".join(missing_kws[:7])
        print(colorize("║", Colors.CYAN) + f"  {colorize('⚠', Colors.YELLOW)} {kw_line[:62]:<64}" + colorize("║", Colors.CYAN))

    # Priority Action Items
    improvements = report.get('improvements', [])
    if improvements:
        print(colorize("╟" + "─" * 68 + "╢", Colors.CYAN))
        print(colorize("║", Colors.CYAN) + f"  {colorize('HIGH-PRIORITY REMEDIATION ITEMS', Colors.BOLD + Colors.RED):<66}" + colorize("║", Colors.CYAN))
        for imp in improvements[:3]:
            print(colorize("║", Colors.CYAN) + f"  {colorize('→', Colors.RED)} {imp[:62]:<64}" + colorize("║", Colors.CYAN))

    print(colorize("╚" + "═" * 68 + "╝", Colors.CYAN) + "\n")


def print_batch_dashboard(summary: Dict[str, Any]):
    """Prints an executive summary table and candidate leaderboard for batch evaluations."""
    total = summary.get("total_files", 0)
    avg_score = summary.get("average_score", 0.0)
    high_score = summary.get("highest_score", 0)
    low_score = summary.get("lowest_score", 0)
    rankings = summary.get("rankings", [])

    print("\n" + colorize("╔" + "═" * 74 + "╗", Colors.CYAN))
    print(colorize("║", Colors.CYAN) + f"   {colorize('AI RESUME ANALYSER', Colors.BOLD + Colors.WHITE)} — {colorize('BATCH RESUME LEADERBOARD & AUDIT SUMMARY', Colors.CYAN):<59}" + colorize("║", Colors.CYAN))
    print(colorize("╠" + "═" * 74 + "╣", Colors.CYAN))
    
    stat_line = f"  Evaluated: {colorize(str(total), Colors.BOLD)} files  |  Average: {colorize(f'{avg_score:.1f}/100', Colors.BOLD + Colors.CYAN)}  |  Top: {colorize(f'{high_score}/100', Colors.BOLD + Colors.GREEN)}  |  Low: {colorize(f'{low_score}/100', Colors.BOLD + Colors.RED)}"
    print(colorize("║", Colors.CYAN) + f"{stat_line:<83}" + colorize("║", Colors.CYAN))
    print(colorize("╠" + "═" * 74 + "╣", Colors.CYAN))

    # Table Header
    print(colorize("║", Colors.CYAN) + f"  {colorize('Rank', Colors.BOLD):<6} {colorize('Candidate / File', Colors.BOLD):<34} {colorize('Score', Colors.BOLD):<11} {colorize('Grade', Colors.BOLD):<7} {colorize('Status', Colors.BOLD):<10}" + colorize("║", Colors.CYAN))
    print(colorize("╟" + "─" * 74 + "╢", Colors.CYAN))

    for rank, res in enumerate(rankings, 1):
        if res.get("status") == "success":
            score = res.get("ats_score", 0)
            g_info = get_grade_info(score)
            fname = res.get("filename", "")[:32]
            score_str = colorize(f"{score:3d}/100", g_info["color"])
            grade_str = colorize(f"[{g_info['grade']:^3}]", Colors.BOLD + g_info["color"])
            status_str = colorize("PASSED" if score >= 70 else "REVIEW", Colors.GREEN if score >= 70 else Colors.YELLOW)
            
            row = f"  #{rank:02d}   {fname:<32} {score_str}   {grade_str}   {status_str}"
            print(colorize("║", Colors.CYAN) + f"{row:<83}" + colorize("║", Colors.CYAN))
        else:
            fname = res.get("filename", "")[:32]
            err_str = colorize("ERROR", Colors.RED)
            row = f"  #{rank:02d}   {fname:<32} {'---':<11} {'[ERR]':<7} {err_str}"
            print(colorize("║", Colors.CYAN) + f"{row:<83}" + colorize("║", Colors.CYAN))

    print(colorize("╚" + "═" * 74 + "╝", Colors.CYAN) + "\n")


def run_cli_audit(
    resume_path: str,
    jd_path: Optional[str] = None,
    output_json_path: Optional[str] = None,
    badge_svg_path: Optional[str] = None,
    quiet: bool = False
) -> Dict[str, Any]:
    """Coordinates CLI audit execution and file outputs."""
    resume_text = parse_resume_file(resume_path)
    
    jd_text = None
    if jd_path:
        if os.path.exists(jd_path):
            with open(jd_path, 'r', encoding='utf-8', errors='ignore') as f:
                jd_text = f.read()
        else:
            raise FileNotFoundError(f"Job description file not found: {jd_path}")

    report = analyze_resume(resume_text=resume_text, job_description=jd_text)
    ats_score = report.get('ats_score', 0)

    # Generate outputs if requested
    if output_json_path:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        if not quiet:
            print(f"✓ JSON audit report saved to: {output_json_path}")

    if badge_svg_path:
        svg_content = generate_svg_badge(ats_score)
        with open(badge_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        if not quiet:
            print(f"✓ Dynamic SVG badge saved to: {badge_svg_path}")

    if not quiet:
        print_single_resume_dashboard(resume_path=resume_path, report=report, jd_path=jd_path)

    return report


def run_batch_cli_audit(
    directory_path: str,
    jd_path: Optional[str] = None,
    output_summary_path: Optional[str] = None,
    quiet: bool = False
) -> Dict[str, Any]:
    """
    Evaluates all supported resume files within a target directory in batch mode.
    Returns aggregate statistics, score distributions, and individual rankings.
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise NotADirectoryError(f"Directory not found or invalid: {directory_path}")

    supported_exts = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    files = [
        os.path.join(directory_path, f)
        for f in os.listdir(directory_path)
        if os.path.splitext(f)[1].lower() in supported_exts and os.path.isfile(os.path.join(directory_path, f))
    ]

    if not files:
        summary = {
            "total_files": 0,
            "average_score": 0.0,
            "results": [],
            "message": "No supported resume files found in directory."
        }
        if output_summary_path:
            with open(output_summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
        return summary

    results = []
    jd_text = None
    if jd_path and os.path.exists(jd_path):
        with open(jd_path, 'r', encoding='utf-8', errors='ignore') as f:
            jd_text = f.read()

    for file_path in files:
        try:
            text = parse_resume_file(file_path)
            report = analyze_resume(resume_text=text, job_description=jd_text)
            score = report.get('ats_score', 0)
            results.append({
                "filename": os.path.basename(file_path),
                "path": file_path,
                "ats_score": score,
                "strengths_count": len(report.get('key_strengths', [])),
                "improvements_count": len(report.get('improvements', [])),
                "status": "success"
            })
        except Exception as e:
            results.append({
                "filename": os.path.basename(file_path),
                "path": file_path,
                "ats_score": 0,
                "error": str(e),
                "status": "error"
            })

    # Sort results by ATS score descending
    results.sort(key=lambda r: r.get("ats_score", 0), reverse=True)
    valid_scores = [r["ats_score"] for r in results if r["status"] == "success"]
    avg_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0.0

    batch_summary = {
        "total_files": len(files),
        "successful_evaluations": len(valid_scores),
        "average_score": avg_score,
        "highest_score": max(valid_scores) if valid_scores else 0,
        "lowest_score": min(valid_scores) if valid_scores else 0,
        "rankings": results
    }

    if output_summary_path:
        with open(output_summary_path, 'w', encoding='utf-8') as f:
            json.dump(batch_summary, f, indent=2)
        if not quiet:
            print(f"✓ Batch evaluation summary saved to: {output_summary_path}")

    if not quiet:
        print_batch_dashboard(batch_summary)

    return batch_summary


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Analyser CLI - Audits resumes for ATS compliance and generates SVG status badges."
    )
    parser.add_argument("resume", nargs="?", help="Path to single resume file (.pdf, .docx, .txt, .md)", default=None)
    parser.add_argument("--batch", "-B", help="Directory path to batch evaluate all resumes", default=None)
    parser.add_argument("--jd", help="Optional path to target job description text file", default=None)
    parser.add_argument("--output", "-o", help="Optional path to save JSON analysis report", default=None)
    parser.add_argument("--badge", "-b", help="Optional path to save dynamic SVG status badge", default=None)
    parser.add_argument("--quiet", "-q", help="Suppress terminal printouts", action="store_true")

    args = parser.parse_args()

    try:
        if args.batch:
            run_batch_cli_audit(
                directory_path=args.batch,
                jd_path=args.jd,
                output_summary_path=args.output,
                quiet=args.quiet
            )
        elif args.resume:
            run_cli_audit(
                resume_path=args.resume,
                jd_path=args.jd,
                output_json_path=args.output,
                badge_svg_path=args.badge,
                quiet=args.quiet
            )
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
