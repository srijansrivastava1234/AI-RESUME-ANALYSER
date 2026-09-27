"""Command-Line Interface (CLI) for Local AI Resume Analyser Batch Evaluation."""

import argparse
import json
import sys
from pathlib import Path
from app.bm25 import calculate_bm25_score
from app.compliance import sanitize_pii

def evaluate_resume_text(resume_text: str, jd_text: str) -> dict:
    """Run a fast deterministic audit on given resume and job description text."""
    clean_text = sanitize_pii(resume_text)
    keywords = [kw.strip().lower() for kw in jd_text.split() if len(kw.strip()) > 3]
    bm25_res = calculate_bm25_score(clean_text, keywords)
    
    return {
        "status": "success",
        "tokens_evaluated": len(clean_text.split()),
        "bm25_keyword_score": bm25_res.get("score", 0.0),
        "sanitized_preview": clean_text[:120] + "...",
    }

def main():
    parser = argparse.ArgumentParser(description="AI Resume Analyser Batch CLI")
    parser.add_argument("--resume", type=str, required=True, help="Path to plain text or markdown resume file")
    parser.add_argument("--jd", type=str, required=True, help="Path to job description text file")
    parser.add_argument("--output", type=str, default=None, help="Optional output JSON filepath")
    
    args = parser.parse_args()
    
    resume_path = Path(args.resume)
    jd_path = Path(args.jd)
    
    if not resume_path.exists():
        print(f"Error: Resume file '{args.resume}' not found.", file=sys.stderr)
        sys.exit(1)
        
    if not jd_path.exists():
        print(f"Error: JD file '{args.jd}' not found.", file=sys.stderr)
        sys.exit(1)
        
    resume_content = resume_path.read_text(encoding="utf-8")
    jd_content = jd_path.read_text(encoding="utf-8")
    
    result = evaluate_resume_text(resume_content, jd_content)
    
    formatted_json = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(formatted_json, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(formatted_json)

if __name__ == "__main__":
    main()
