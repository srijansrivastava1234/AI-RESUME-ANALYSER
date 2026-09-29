"""
Module: latex_parser.py
Purpose: Direct LaTeX (.tex) resume parser, AST token extractor, and ATS sanitizer.
Strips math mode, LaTeX command macros, environments, and converts ligatures to plain text.
"""

import re
import unicodedata
from typing import Dict, Any, List


def strip_latex_comments(source: str) -> str:
    """Removes LaTeX comment lines (% ...) while preserving escaped percent signs (\\%)."""
    return re.sub(r'(?<!\\)%.*$', '', source, flags=re.MULTILINE)


def parse_latex_resume(source: str) -> Dict[str, Any]:
    """
    Parses raw LaTeX resume source code into clean ATS-parseable plain text and structured sections.
    """
    clean = strip_latex_comments(source)

    # Extract common section headers (\section{...}, \cvsection{...}, \textbf{...})
    sections = {}
    current_section = "HEADER"
    sections[current_section] = []

    lines = clean.splitlines()
    for line in lines:
        sec_match = re.search(r'\\(?:cv)?section\*?\{([^}]+)\}', line, re.IGNORECASE)
        if sec_match:
            current_section = sec_match.group(1).strip().upper()
            if current_section not in sections:
                sections[current_section] = []
            continue
        
        # Remove standard LaTeX commands (\textbf{foo} -> foo, \textit{bar} -> bar)
        processed_line = re.sub(r'\\(?:textbf|textit|underline|emph|textsf|textsc)\{([^}]*)\}', r'\1', line)
        # Remove href/url commands: \href{url}{text} -> text
        processed_line = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', processed_line)
        # Remove environments (\begin{itemize}, \item, \end{itemize})
        processed_line = re.sub(r'\\begin\{[^}]*\}|\\end\{[^}]*\}', '', processed_line)
        processed_line = re.sub(r'\\item\s*', '• ', processed_line)
        # Remove standalone commands and macros (\vspace{...}, \\, \hline)
        processed_line = re.sub(r'\\[a-zA-Z]+(?:\*?\[[^\]]*\])?(?:\*?\{[^}]*\})?', '', processed_line)
        processed_line = re.sub(r'\\\\|\\hline|\\quad|\\qquad', ' ', processed_line)
        # Unescape special characters (\& -> &, \$ -> $, \% -> %)
        processed_line = re.sub(r'\\([&%$#_{}])', r'\1', processed_line)
        
        # Normalize Unicode ligatures
        processed_line = unicodedata.normalize("NFKD", processed_line)
        
        stripped = processed_line.strip()
        if stripped:
            sections[current_section].append(stripped)

    # Flatten plain text
    all_text_lines = []
    for sec_name, sec_lines in sections.items():
        if sec_name != "HEADER":
            all_text_lines.append(f"\n{sec_name}\n")
        all_text_lines.extend(sec_lines)

    plain_text = "\n".join(all_text_lines).strip()

    return {
        "plain_text": plain_text,
        "sections": {k: "\n".join(v) for k, v in sections.items() if v},
        "section_names": [k for k in sections.keys() if sections[k]],
        "token_count": len(plain_text.split()),
        "has_standard_sections": any(s in sections for s in ["EXPERIENCE", "SKILLS", "EDUCATION", "WORK EXPERIENCE"])
    }
