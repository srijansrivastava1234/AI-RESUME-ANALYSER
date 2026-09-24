# Changelog

All notable changes to the **AI Resume Analyser** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-09-24

### Added
- **Top 9 Flagship Technical Contributions Catalog**: Authored `CONTRIBUTIONS_TOP9.md` and `contributions_top9.txt` synthesizing Google/IBM X-Y-Z quantifiable achievements, mathematical formulations, and ATS system mechanics.
- **Top 9 Architectural Integrity Test Suite**: Created `backend/tests/test_top9_integrity.py` providing end-to-end regression validation across all 9 core architectural pillars.
- **Runtime Environment & Configuration Validator**: Implemented `app.config_validator` and `test_config_validator.py` with runtime sanity auditing, API key readiness detection, and system health reporting.
- **High-Performance Parser Utilities & Cache**: Engineered `app.parser_utils` and `test_parser_utils.py` featuring `@lru_cache` string sanitization, fast tokenization, and precompiled regex operations.
- **Latency & Scalability Benchmark Regression Suite**: Added `backend/tests/test_performance_benchmarks.py` enforcing sub-25ms SLA thresholds across deterministic ATS parsing engines.
- **Expanded Developer & Contribution Standards**: Updated `CONTRIBUTING.md` with the 9-Pillar Architecture & Quality Checklist and conventional commit specifications.
- **OpenAPI 3.1 Metadata & Route Tags**: Updated FastAPI application metadata with version 3.1.0 and modular route tags.

---

## [2.4.0] - 2026-09-22

### Added
- **Flesch-Kincaid & Gunning Fog Readability Metrics Engine**: Implemented `app.readability` calculating Flesch Reading Ease, Flesch-Kincaid Grade Level, and Gunning Fog Index to evaluate linguistic clarity and target the optimal Grade 8-12 executive comprehension sweet spot.
- **Passive Voice Density & Active Voice Ratio Detector**: Engineered `app.voice_detector` evaluating syntactic constructions to enforce a >=90% Active Voice Ratio and provide actionable power verb transformation recommendations.
- **Weak Filler Words & Corporate Cliché Eliminator**: Created `app.cliche_detector` identifying overused buzzwords ('rockstar', 'team player', 'outside the box') and mapping them directly to substantiated technical alternatives.
- **Multi-Dimensional Metric Diversity Classifier**: Developed `app.metric_diversity` categorizing quantified accomplishments into Financial, Percentage, Scale/Volume, Velocity/Latency, and Leadership dimensions to evaluate outcome breadth.
- **Enterprise ATS File Naming Standard Auditor**: Formulated `app.filename_auditor` screening against whitespace breakage, special characters (`#`, `%`), and generic naming, producing standardized canonical filenames (`FirstName_LastName_Resume.pdf`).
- **Skill Recency & Career Tenure Decay Engine**: Built `app.skill_recency` differentiating contemporary active frameworks (Docker, FastAPI, Kubernetes) from decayed legacy tech stacks (AngularJS 1.x, ColdFusion, Flash).
- **Bullet Point Sweet-Spot Scannability Auditor**: Implemented `app.bullet_length` auditing word counts against the 15-25 words sweet spot to maximize recruiter eye-tracking engagement.
- **Executive Value Summary vs Outdated Objective Classifier**: Developed `app.summary_classifier` identifying outdated candidate-centric Objective Statements and transforming them into modern Value Propositions.
- **Confidential Salary & CTC Disclosure Prevention**: Engineered `app.salary_detector` detecting inadvertent personal compensation, CTC, or hourly wage disclosures.
- **Canonical Portfolio & Digital Identity Link Security Auditor**: Architected `app.portfolio_validator` verifying HTTPS encryption on LinkedIn and GitHub handles and flagging unpopulated placeholder links.
- **10 Dedicated FastAPI REST Endpoints**: Exposed `/api/audit-readability`, `/api/audit-voice`, `/api/audit-cliches`, `/api/audit-metric-diversity`, `/api/audit-filename`, `/api/audit-skill-recency`, `/api/audit-bullet-lengths`, `/api/audit-summary-style`, `/api/audit-salary-disclosures`, and `/api/audit-portfolio-links` with SlowAPI rate limiting.
- **Master Analyzer Pipeline Deep Diagnostic Integration**: Seamlessly integrated all 10 diagnostic modules into the primary `analyze_resume` pipeline.
- **Automated Test Suite Expansion to 267+ Tests**: Created 10 new test suites (`test_readability.py`, `test_voice_detector.py`, `test_cliche_detector.py`, `test_metric_diversity.py`, `test_filename_auditor.py`, `test_skill_recency.py`, `test_bullet_length.py`, `test_summary_classifier.py`, `test_salary_detector.py`, `test_portfolio_validator.py`, `test_api_v24.py`, `test_analyzer_v24.py`).
- **Expanded Master Technical Contributions Inventory**: Documented 15 new achievements (#78 to #92) in `contributions.txt` and refreshed `contributions_top15.txt`.

---

## [2.3.0] - 2026-09-21

### Added
- **ATS Section Flow & Structural Ordering Auditor**: Implemented `app.section_flow` evaluating sequential resume flow against enterprise ATS parsing heuristics and recruiter F-pattern scanline reading ergonomics, automatically adjusting precedence rules for Early-Career vs Experienced candidate profiles.
- **Action Verb Dynamism & Repetitive Fatigue Scorer**: Engineered `app.action_verb_analyzer` computing the Action Verb Variety Ratio (AVVR), categorizing opening verbs into Executive, Engineering, Operational, and Weak/Passive tiers, penalizing repetitive opening fatigue (>2x), and providing dynamic power-verb replacements.
- **Multi-Page Visual Budget & Spillover Hazard Analyzer**: Formulated `app.page_budget_analyzer` calculating physical line count approximations and token density budgets against 1-page and 2-page targets, detecting dangerous trailing spillover hazards (1.05–1.20 pages) that create near-empty orphan pages in recruiter PDF previewers.
- **Dedicated REST API Endpoints & Master Analyzer Pipeline Enrichment**: Exposed `POST /api/audit-section-flow`, `POST /api/audit-action-verbs`, and `POST /api/audit-page-budget` in `app.main` with SlowAPI rate throttling (30/minute), and seamlessly enriched the primary `POST /api/analyze` pipeline to return comprehensive section flow, verb dynamism, and page budget telemetry.
- **Interactive Section Flow, Action Verb & Page Budget UI Workspace**: Added interactive visual cards in `HygieneCard.jsx` and `TabsPanel.jsx` displaying sequence flow breadcrumbs, action verb tier distribution badges, variety percentages, and multi-page budget safety indicators.
- **Automated Test Suite Expansion to 237 Tests with 90% Code Coverage**: Added `test_section_flow.py`, `test_action_verb_analyzer.py`, `test_page_budget_analyzer.py`, and `test_api_v23.py`, scaling the test suite from 221 to 237 tests with 90% codebase coverage in pytest-cov.
- **Expanded Master Technical Contributions Inventory**: Documented 8 new technical achievements in `contributions.txt` covering section flow sequence, verb fatigue algorithms, and multi-page layout budgeting.

---

## [2.2.0] - 2026-09-20

### Added
- **Okapi BM25+ Lexical Retrieval & Term Saturation Engine**: Implemented `app.bm25_scorer` providing Okapi BM25+ ($k_1=1.2, b=0.75, \delta=1.0$) with Robertson-Spärck Jones IDF, modeling asymptotic term frequency saturation to penalize keyword stuffing, and enforcing length normalization against a 450-token empirical baseline with granular per-term score contribution breakdowns.
- **Candidate Contact Coordinates & Link Security Auditor**: Formulated `app.contact_validator` validating emails against RFC 5322 specifications, screening out disposable temporary mailboxes (Mailinator, GuerrillaMail), standardizing international phone numbers to ITU-T E.164 (`+1`, `+91`, `+44`), and auditing external profile links for HTTPS encryption and blacklisted URL redirect shorteners.
- **Hard vs Soft Skills Taxonomy Classifier & Buzzword Dilution Defense**: Architected `app.skill_classifier` separating verifiable technical proficiencies from subjective soft buzzwords ('team player', 'fast learner', 'self-starter'), calculating the Hard-to-Soft Ratio ($R_{skill}$), flagging buzzword dilution (>30% soft), and cross-auditing hard skills against Work Experience accomplishment bullets.
- **Dedicated High-Throughput REST APIs**: Exposed `POST /api/audit-bm25`, `POST /api/audit-contact`, and `POST /api/classify-skills` endpoints in `app.main` with SlowAPI rate throttling (30/minute), and enriched core `POST /api/analyze` response payloads to seamlessly return BM25+, contact security, and skill taxonomy diagnostics.
- **Interactive BM25+ Relevance, Contact Security & Skill Taxonomy UI**: Added Okapi BM25+ saturation meters and Hard vs Soft skill ratio breakdown cards in `TabsPanel.jsx`, alongside an RFC 5322 and HTTPS link security audit section in `HygieneCard.jsx`.
- **Automated Test Suite Scaling from 184 to 221 Tests**: Created `backend/tests/test_bm25_scorer.py`, `backend/tests/test_contact_validator.py`, `backend/tests/test_skill_classifier.py`, `backend/tests/test_api_v22.py`, and `backend/tests/test_analyzer_v22.py`, scaling test coverage to 221 unit and integration tests across 26 test modules with a 90% codebase coverage threshold in pytest-cov.
- **Expanded Master 77 Key Technical Contributions Inventory**: Documented 15 new technical contributions (#63 to #77) in `contributions.txt`, refreshed `contributions_top15.txt`, and updated system architecture and metrics in `README.md`.

---

## [2.1.0] - 2026-09-18

### Added
- **Recursive XY-Cut Layout Linearization & Scanline Interleaving Detector**: Implemented `app.layout_linearizer` simulating horizontal and vertical whitespace projection valleys, detecting column gutter collapses (<12pt), ASCII border intersections, and scanline interleaving traps where sidebars concatenate into job titles in legacy parsers (Taleo, older Workday), returning a 0–100 Linearization Safety Index with simulated scrambled text previews.
- **Career Chronology & Non-Canonical Date Range Normalizer**: Engineered `app.chronology` standardizing dates to ISO-compatible months, calculating non-duplicative cumulative Years of Experience (YoE) across overlapping tenures, detecting employment gaps (>90 days) with recruiter talking points, and penalizing ambiguous seasonal or relative date tokens ('Spring 2021', '2 years ago').
- **ISO 19005-2 PDF/A Text Layer, CMap Integrity & Ligature Normalizer**: Formulated `app.font_integrity` detecting Unicode Private Use Area (PUA) codepoints (`\uE000-\uF8FF`), decode replacement characters (`\uFFFD`), soft hyphens (`\u00AD`), and zero-width spaces, while automatically decomposing typographic ligatures (fi, fl, ff, ffi, ffl, oe, ae) into plain ASCII to ensure exact keyword retrieval in ATS Boolean filters.
- **High-Throughput Dedicated REST APIs**: Exposed `POST /api/audit-layout`, `POST /api/audit-chronology`, and `POST /api/audit-font-integrity` endpoints in `app.main` with SlowAPI rate limiting, and enriched core `POST /api/analyze` response payloads to seamlessly return layout, chronology, and font integrity diagnostics.
- **Interactive Layout, Chronology & Typography UI Workspace**: Designed a dedicated "Layout & Chronology" panel in `TabsPanel.jsx` featuring Recursive XY-Cut scanline hazard meters, simulated legacy ATS text scramble viewers, visual career timeline chips with gap alerts, and typographic ligature recovery cards.
- **Automated Unit & Integration Test Suites Scaling to 184 Tests**: Created `backend/tests/test_layout_linearizer.py`, `backend/tests/test_chronology.py`, `backend/tests/test_font_integrity.py`, and `backend/tests/test_api_v21.py`, advancing the test suite from 151 to 184 tests with a 90% code coverage threshold in pytest-cov.
- **Expanded Master 62 Key Technical Contributions Inventory**: Documented 10 new contributions (#53 to #62) in `contributions.txt`, updated `contributions_top15.txt`, and refreshed system architecture in `README.md`.

---

## [2.0.0] - 2026-09-17

### Added
- **Seniority Target Ratio & Bullet Distribution Profiler**: Formulated `app.seniority_profiler` calibrating career accomplishments against engineering seniority expectations: Junior (70% XYZ), Mid-Level (80% XYZ), Senior (85% XYZ), Staff (60% XYZ / 40% Strategic), and Executive (50% XYZ / 50% Strategic), computing a 0–100 Seniority Alignment Index and detecting strategic cross-org narrative.
- **EEOC & NYC Local Law 144 Blind Review PII Redaction Engine**: Architected `app.redaction` deterministically anonymizing candidate names, emails, phone numbers, postal locations, social profiles, and **graduation year age proxies** to eliminate algorithmic bias and produce compliant blind review dossiers per NYC LL 144 and EU AI Act Article 10.
- **Dedicated Seniority & Privacy REST APIs**: Exposed `POST /api/seniority-profile` and `POST /api/redact-pii` endpoints in `app.main` with SlowAPI rate limits, providing sub-5ms client-side anonymization and ratio audits with zero external LLM token expenditure.
- **Interactive Seniority Matrix & Blind Review UI Panel**: Designed interactive Seniority Target Calibrator and EEOC/NYC LL 144 Blind Review Synthesizer in `TabsPanel.jsx` featuring real-time ratio progress bars, redacted entity pill counters, and one-click blind dossier clipboard export.
- **100% Coverage Seniority & Privacy Unit Test Suites**: Created `backend/tests/test_seniority_profiler.py` and `backend/tests/test_redaction.py` asserting ratio accuracy, passive duty penalties, demographic proxy masking, and 100% preservation of technical tools and metrics.
- **Expanded Master 52 Key Technical Contributions Inventory**: Documented 7 new contributions (#46 to #52) in `contributions.txt` across Full XYZ bullets, 1-line resume items, LaTeX blocks, and STAR talking points.
- **151 Automated Tests with 89% Code Coverage Quality Gate**: Scaled automated test suite to 151 unit and integration tests across 16 test modules with an 89% pytest-cov code coverage threshold.

---

## [1.9.0] - 2026-09-16

### Added
- **White-Font & Invisible Ink ATS Hack Spam Detector**: Engineered `app.hack_detector` auditing documents for zero-contrast text (`#ffffff`, `opacity: 0`), microscopic typography (`font-size <= 1px`), off-canvas containers (`left: -9999px`), and invisible zero-width Unicode injection (`\u200B-\uFEFF`) to prevent automated ATS spam disqualification.
- **Workday & Taleo Canonical Section Header Normalizer**: Implemented `app.header_normalizer` mapping non-canonical or creative headings (e.g. "Where I've Been", "My Toolkit", "Things I Built") into enterprise ATS schemas with automated missing mandatory section alerts.
- **Multi-Lingual Semantic Token Density & Stopword Filter**: Developed `app.token_density` supporting English, Spanish, Portuguese, French, and German stopwords to compute Type-Token Ratio (TTR) and content signal-to-noise density.
- **Vanity Metric vs Business Outcome Disambiguator**: Formulated `app.metric_validator` calibrating Google/IBM quantifiable metric scoring to differentiate true business outcomes ($ revenue, latency, SLA) from vanity activity counts ("attended 50 meetings", "wrote 10,000 lines of code"), enforcing the canonical -20 pt vanity deduction.
- **Standalone Security, Header & Metric Diagnostic REST APIs**: Exposed `POST /api/detect-hacks`, `POST /api/audit-headers`, `POST /api/token-density`, and `POST /api/validate-metric` in `app.main` with SlowAPI rate throttling and Pydantic validation.
- **Real-Time Anti-Spam Security Shield & Header Alignment UI**: Added dynamic ATS Spam Shield indicators in `Header.jsx`, comprehensive contrast and legibility audit cards in `HygieneCard.jsx`, and Workday/Taleo canonical mapping chips in `TabsPanel.jsx`.
- **Expanded Master 45 Key Technical Contributions Inventory**: Documented 10 new technical achievements (#36 to #45) in `contributions.txt` across Full XYZ bullets, 1-line resume items, LaTeX blocks, and STAR talking points.
- **Refreshed Top 15 Technical Contributions Showcase**: Updated `contributions_top15.txt` with latest high-impact accomplishments, updated LaTeX snippets, and recruiter interview points.
- **Scaled Automated Test Suite to 133 Tests**: Expanded test suite to 133 unit and integration tests across `test_hack_detector.py`, `test_header_normalizer.py`, `test_token_density.py`, `test_metric_validator.py`, and `test_api.py`, achieving an 88%+ test coverage threshold in pytest-cov.

---

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
