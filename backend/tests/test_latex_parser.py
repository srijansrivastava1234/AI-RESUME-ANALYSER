"""
Unit tests for LaTeX resume parser.
"""

from app.latex_parser import parse_latex_resume, strip_latex_comments

SAMPLE_TEX = r"""
\documentclass{article}
\begin{document}

% Candidate Profile Header
\textbf{Johnathan Wick} \\
\href{mailto:john@example.com}{john@example.com} | 555-0199 | New York, NY

\section{Experience}
\textbf{Principal Architect} -- Continental Corp (2020--Present)
\begin{itemize}
    \item Engineered distributed microservices with Go \& Python saving \$500k annually.
    \item Scaled Kubernetes cluster to handle 50k requests/sec.
\end{itemize}

\section{Skills}
Python, Go, Docker, Kubernetes, AWS, PostgreSQL, Redis

\section{Education}
B.S. Computer Science, MIT (2018)

\end{document}
"""

def test_strip_latex_comments():
    raw = "Code % this is a comment\nNext line \\% not a comment"
    stripped = strip_latex_comments(raw)
    assert "this is a comment" not in stripped
    assert "not a comment" in stripped

def test_parse_latex_resume():
    res = parse_latex_resume(SAMPLE_TEX)
    assert "Johnathan Wick" in res["plain_text"]
    assert "john@example.com" in res["plain_text"]
    assert "EXPERIENCE" in res["section_names"]
    assert "SKILLS" in res["section_names"]
    assert "EDUCATION" in res["section_names"]
    assert "Kubernetes" in res["plain_text"]
    assert "$500k" in res["plain_text"]
    assert "&" in res["plain_text"]
    assert res["token_count"] > 10
