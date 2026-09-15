# Changelog

All notable changes to the **AI Resume Analyser** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2026-09-15

### Added
- **Reciprocal Rank Fusion (RRF) Multi-Metric Candidate Scoring Engine**: Implemented `compute_rrf_from_rank_lists()` and `fuse_candidate_evaluations()` in `app.rrf_engine` fusing keyword recall, XYZ score, formatting hygiene, and readability into stable, normalized candidate leaderboards without scale distortion.
- **Technical Acronym & Domain Synonym Resolution Graph**: Created `app.acronyms` providing bidirectional translation across industry tech stacks (e.g. K8s $\leftrightarrow$ Kubernetes, TS $\leftrightarrow$ TypeScript, AWS $\leftrightarrow$ Amazon Web Services) and integrated synonym-aware matching into `app.keywords`.
- **Recruiter 6-Second First-Third (Upper 30% Viewport) Precision Scanner**: Architected `audit_first_third_viewport()` in `app.viewport` quantifying accomplishment front-loading, metric density, and active leadership verbs within the recruiter's initial 6.0-7.4s glance.
- **Adverse Impact & EEOC Four-Fifths Safe Harbor Auditor**: Developed `app.adverse_impact` evaluating selection rate parity across candidate cohorts ($IR \ge 0.80$) and certifying 100% deterministic rule arithmetic per NYC Local Law 144.
- **Standalone Viewport, Synonym & Adverse Impact REST APIs**: Exposed `POST /api/viewport-audit`, `POST /api/expand-keywords`, and `POST /api/adverse-impact` in `app.main` protected by SlowAPI rate limits and Pydantic validation.
- **Interactive First-Third Viewport Telemetry & Acronym Mapping UI**: Added a dedicated Viewport Precision card in `HygieneCard.jsx` and an interactive Technical Acronym & Domain Synonym Mapping pill matrix in `TabsPanel.jsx`.
- **Master 35 Key Technical Contributions Inventory**: Documented 10 new technical achievements (#26 to #35) in `contributions.txt` and refreshed `contributions_top15.txt` with Full XYZ bullets, 1-line resume items, LaTeX blocks, and STAR talking points.
- **Scaled Automated Test Suite to 101 Tests**: Expanded backend test matrix to 101 unit and integration tests achieving 88%+ total codebase coverage in pytest-cov.

---

## [1.7.0] - 2026-09-14

### Added
- **Curated Top 15 Technical Contributions Inventory**: Formulated and published `contributions_top15.txt` curating the highest-signal technical contributions from the 25-point master inventory across Full XYZ, 1-Line Bullets, LaTeX snippets, and STAR interview talking points.
- **Action Verb Diversity Engine & Repetition Penalty**: Formulated `evaluate_bullet_verb_diversity()` in `app.xyz_scorer` and exposed `POST /api/verb-diversity` with SlowAPI rate limiting to audit repetitive verbs and compute a 0-100 diversity index.
- **Quantitative Readability Index**: Implemented `calculate_readability_metrics()` in `app.hygiene` calculating Flesch-Kincaid Grade Level and Gunning Fog indices embedded within the ATS hygiene scorecard.
- **Multi-Model Prompt Synthesis Engine**: Expanded `app.agent_prompt` with tailored prompt architectures for Anthropic Claude 3.5 Sonnet (XML tags), OpenAI GPT-4o, and Cursor Composer.
- **Interactive Model Selector in Prompt Exporter**: Added interactive prompt model switching in `TabsPanel.jsx` allowing 1-click clipboard export for Claude, GPT-4o, Cursor, or Universal Markdown.
- **Readability & Cognitive Skim UI Card**: Added a dedicated readability metrics panel in `HygieneCard.jsx` displaying Flesch-Kincaid Grade, Gunning Fog index, and average sentence length.
- **Performance Optimization via Precompiled Regexes**: Precompiled skill taxonomy patterns in `app.keywords` for sub-millisecond keyword classification throughput.
- **Expanded Test Suite to 75+ Automated Tests**: Added comprehensive unit and integration tests across `test_agent_prompt.py`, `test_xyz_scorer.py`, `test_hygiene.py`, `test_compliance.py`, and `test_api.py`.

---

## [1.6.0] - 2026-09-13

### Added
- **Deterministic 4-Pillar ATS Compliance & Letter Grade Engine**: Formulated and implemented `app.compliance` combining Keywords & Hard Skills (40%), Google/IBM X-Y-Z Impact (30%), Structural Parseability (15%), and Reading Density/Word Budget (15%) with executive letter grades (A+, A, B, C, D) and percentile benchmarking.
- **Regulatory Safe Harbor Verification (EU AI Act & NYC Local Law 144)**: Added automated legal compliance screening certifying 100% deterministic rule arithmetic per EU AI Act Regulation (EU) 2024/1689 (Annex III & Article 86 Right to Explanation) and zero demographic proxy variables for NYC LL 144 AEDT bias safe harbor.
- **Metric False-Positive Disambiguation & Binary Impact Detection**: Engineered regex guards filtering out software versions (`Python 3.11`), network ports (`Port 8080`), and RFC/ISO standards from false metric inflation while recognizing true-positive binary achievements (`zero downtime`, `patent granted`).
- **Agent-Native BYOK Prompt Synthesis Engine**: Architected `app.agent_prompt` generating zero-hallucination markdown prompts configured for frontier external LLMs (Claude 3.5 Sonnet, GPT-4o, Cursor) adhering to candidate Bring-Your-Own-Key (BYOK) privacy governance.
- **Standalone Compliance & Prompt REST APIs**: Exposed `POST /api/compliance-audit` and `POST /api/agent-prompt` protected by SlowAPI rate limiting, and enriched core `POST /api/analyze` response with automatic compliance scorecards.
- **Interactive 4-Pillar Compliance & Safe Harbor UI**: Added a dedicated "Compliance & Safe Harbor" tab in `TabsPanel.jsx` featuring dynamic letter grade badges, 4-pillar score breakdown cards, regulatory safe harbor cards, reading density meters, and one-click BYOK prompt clipboard export.
- **65+ Automated Tests & Pytest-Cov Quality Gate**: Scaled automated test suite to 65+ tests in `backend/tests/test_compliance.py` achieving 86%+ total codebase coverage.
- **25 Key Technical Contributions**: Expanded `contributions.txt` and `README.md` to 25 technical achievements across Full Bullets, 1-Line Bullets, LaTeX snippets, and STAR interview points.

---

## [1.5.0] - 2026-09-11

### Added
- **Deterministic Google/IBM X-Y-Z Mathematical Scoring Engine**: Implemented `app.xyz_scorer` evaluating bullet statements across Action Verbs ($w=0.25$), Quantifiable Metrics ($w=0.45$), and Technical Tooling ($w=0.30$) with automated deductions for passive duty statements (-40 pts), cognitive overload/verbosity (-25 pts), and under-detailed text (-30 pts).
- **Interactive Google/IBM XYZ Bullet Impact Lab UI**: Added `BulletImpactLab.jsx` with real-time mathematical score gauge, seniority calibration selector (Junior, Mid, Senior, Staff), detected verb/metric/tooling chips, penalty breakdown tags, and one-click Gemini AI optimization.
- **Standalone Bullet Scoring REST API**: Exposed `POST /api/score-bullet` in `app.main` with SlowAPI rate limiting (20/min), Pydantic schema validation, and sub-5ms local evaluation time.
- **ATS Document Layout Linearization & Gutter Collision Detection**: Added `audit_layout_linearization()` in `app.parser` detecting multi-column whitespace gutters and table borders to protect against reading-order corruption in Workday, Taleo, and Ashby ATS pipelines.
- **Automated Test Matrix Quality Gate**: Expanded automated test suite to 55+ unit and integration tests across `test_xyz_scorer.py`, `test_parser.py`, and `test_api.py`, achieving an 88%+ code coverage threshold.
- **Expanded 20 Technical Contributions**: Scaled `contributions.txt` and `README.md` from 15 to 20 comprehensive technical achievements with XYZ bullets, 1-line resume lines, LaTeX snippets, and STAR interview talking points.

---

## [1.4.0] - 2026-09-10

### Added
- **Multi-Resume Comparison Engine**: Implemented `app.comparator` and exposed `POST /api/compare` allowing concurrent evaluation and ranking of 2-5 candidate resumes against target job descriptions.
- **ATS Formatting Hygiene Evaluator**: Created `app.hygiene` and exposed `POST /api/hygiene` auditing contact info (email, phone, LinkedIn, GitHub), standard section headers, bullet density, and computing a 100-point hygiene score.
- **Candidate Comparison Leaderboard UI**: Added `ComparePanel.jsx` and mode switcher in header enabling side-by-side candidate ranking with gold/silver/bronze rank badges, score differentials, and strengths accordions.
- **ATS Formatting Hygiene Card**: Added `HygieneCard.jsx` inside the overview tab displaying contact detection chips, section audit checklist, and actionable structural advice.
- **SlowAPI Defensive Rate Limiting**: Added IP-based rate limiting (10/min for `/api/analyze`, 5/min for `/api/compare`, 20/min for `/api/optimize-bullet`) with RFC-compliant HTTP 429 JSON responses.
- **Structured JSON Logging & Request Tracing**: Created `app.logging_config` featuring JSON log output, microsecond timestamps, and custom `X-Request-ID` correlation headers across all endpoints.
- **Frontend Performance Utilities**: Created `frontend/src/utils/performance.js` with `calculateKeywordDensity`, `debounce`, and `memoize` helpers; integrated `useMemo` in `TabsPanel.jsx` to eliminate typing latency in sandbox mode.
- **Pytest-Cov Test Coverage in CI**: Integrated `pytest-cov` in `.github/workflows/ci.yml` and `pytest.ini`, establishing 78%+ test coverage across parsers, analyzers, rules, comparators, hygiene, and APIs.
- **Expanded 15 Technical Contributions**: Scaled `contributions.txt` and `README.md` from 7 to 15 comprehensive technical achievements with XYZ bullets, 1-line resume items, LaTeX snippets, and STAR talking points.

---

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
