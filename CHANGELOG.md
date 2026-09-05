# Changelog

All notable changes to the **AI Resume Analyser** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-09-05

### Added
- **Standalone Bullet Optimizer Endpoint**: Exposed `/api/optimize-bullet` endpoint for on-demand transformation of weak resume bullets into high-impact Google XYZ statements.
- **Categorized Technical Skill Extraction**: Built domain taxonomy keyword extractor in `app.keywords` categorizing skills across Languages, Frameworks, Cloud & DevOps, Databases, and Architecture.
- **Multi-Format Report Exporters**: Integrated one-click downloads for structured JSON data and formatted plain-text ATS summaries alongside Markdown export and PDF printing.
- **Instant Sample Resume Loader**: Added "Try Sample" action in Dropzone to load a realistic Software Engineer profile for zero-friction demo testing.
- **Continuous Integration Workflow**: Created GitHub Actions CI workflow testing across Python 3.11/3.12 and Node.js 20/22 matrices.
- **FastAPI TestClient Integration Tests**: Added test coverage for API routing, error conditions, file format enforcement, and security headers.
- **Job Description Counter Badge**: Added live word and character counters with quick-clear and shortcut hints.
- **Open-Source Contributing Guide**: Added `CONTRIBUTING.md` with development setup, testing commands, and commit conventions.

---

## [1.2.0] - 2026-09-03

### Added
- **Automated Test Suite**: Added comprehensive pytest unit testing for PDF/DOCX/TXT text parsers and heuristic fallback rule engines.
- **Security & Timing Headers Middleware**: Integrated `X-Process-Time`, `X-Content-Type-Options: nosniff`, and `X-Frame-Options: DENY` HTTP response headers.
- **Global Keyboard Shortcuts**: Enabled `Ctrl+Enter` / `Cmd+Enter` keyboard binding to trigger resume audit directly from any view.
- **Test Dependencies**: Configured `pytest` and `httpx` in backend `requirements.txt`.

### Changed
- **Documentation**: Updated `README.md` with test execution guides and keyboard shortcut instructions.

---

## [1.1.0] - 2026-09-01

### Added
- **7 Core Technical Contributions**: Added comprehensive documentation in `contributions.txt` including full XYZ bullet points, 1-line resume entries, LaTeX snippets, and STAR interview talking points.
- **Cross-Platform Normalization**: Added `.gitattributes` to standardize LF line endings across operating systems.
- **Enhanced OpenAPI Documentation**: Added API title, descriptive metadata, and route documentation to FastAPI backend.
- **Multi-Format Ingestion**: Full support for PDF, DOCX, and TXT parsing with regex-based token optimization.
- **Dual-Engine Scoring**: Integration of Gemini 1.5 Flash structured JSON outputs with an offline heuristic fallback engine.

### Improved
- **Token Efficiency**: Document extraction pipelines reduce payload overhead by up to 30% via regex whitespace normalization.
- **User Interface**: Glassmorphic dark dashboard with responsive SVG gauge meters, keyword density chips, and tabbed audit breakdown.
- **History Management**: Zero-database client-side caching with browser LocalStorage and instant Markdown report export.

---

## [1.0.0] - 2026-08-28

### Initial Release
- Initial release of AI Resume Analyser full-stack application.
- FastAPI backend with PyPDF text extraction.
- React 19 + Vite frontend with live ATS compatibility scoring.
