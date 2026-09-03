# Changelog

All notable changes to the **AI Resume Analyser** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
