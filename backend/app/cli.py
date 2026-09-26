"""
Module: cli.py
Purpose: Standalone Command-Line Interface and Dynamic SVG Badge Generator
for automated ATS resume auditing and CI/CD pull request integration.
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any

from app.parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from app.analyzer import analyze_resume


def generate_svg_badge(ats_score: int, label: str = "ATS Score") -> str:
    """
    Generates a crisp, retina-ready Shields.io-style SVG status badge.
    """
    score = max(0, min(100, int(ats_score)))
    
    if score >= 85:
        bg_color = "#10b981" # Emerald Green
        grade = "A+" if score >= 95 else "A"
    elif score >= 70:
        bg_color = "#38bdf8" # Sky Blue
        grade = "B"
    elif score >= 55:
        bg_color = "#f59e0b" # Amber Yellow
        grade = "C"
    else:
        bg_color = "#ef4444" # Rose Red
        grade = "D"

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
        print("\n" + "=" * 60)
        print(f"          ATS RESUME AUDIT REPORT")
        print("=" * 60)
        print(f"File Analyzed: {os.path.basename(resume_path)}")
        print(f"Overall ATS Score: {ats_score}/100")
        print("-" * 60)
        
        print("\n[CORE METRICS]")
        for m in report.get('metrics', []):
            print(f"  • {m.get('name', 'Metric')}: {m.get('score', 0)}/100")
            print(f"    Feedback: {m.get('feedback', '')}")

        strengths = report.get('key_strengths', [])
        if strengths:
            print("\n[KEY STRENGTHS]")
            for s in strengths:
                print(f"  ✓ {s}")

        missing_kws = report.get('keywords', {}).get('missing', [])
        if missing_kws:
            print("\n[TOP MISSING KEYWORDS]")
            print(f"  ⚠️  {', '.join(missing_kws[:8])}")

        print("\n" + "=" * 60 + "\n")

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
        print("\n" + "=" * 60)
        print(f"          BATCH RESUME AUDIT SUMMARY")
        print("=" * 60)
        print(f"Evaluated Files: {len(files)} | Average ATS Score: {avg_score}/100")
        print("-" * 60)
        for rank, res in enumerate(results, 1):
            if res["status"] == "success":
                print(f"  #{rank:02d} [{res['ats_score']:3d}/100] {res['filename']}")
            else:
                print(f"  #{rank:02d} [ERR]     {res['filename']} - {res.get('error', '')}")
        print("=" * 60 + "\n")

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

