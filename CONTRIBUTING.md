# Contributing to AI Resume Analyser

Thank you for your interest in contributing to **AI Resume Analyser**! We welcome bug fixes, performance optimizations, new features, and documentation improvements.

---

## 🛠️ Development Setup

### Prerequisites
- **Python 3.10+** (Tested on 3.11, 3.12, and 3.14)
- **Node.js 18+** / npm 9+
- **Google Gemini API Key** (Optional for local testing; the backend operates in simulation/heuristic mode automatically if no key is present)

---

### 1. Backend Setup (FastAPI)

```bash
# Navigate to repository root
cd AI-RESUME-ANALYSER

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the development server
uvicorn backend.app.main:app --reload --port 8000
```

The interactive OpenAPI documentation will be accessible at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### 2. Frontend Setup (React 19 & Vite)

```bash
cd frontend
npm install
npm run dev
```

The web dashboard will be available at `http://localhost:5173`.

---

## 🧪 Running Automated Tests & Benchmarks

We maintain comprehensive automated test suites for document parsing, heuristic scoring, keyword taxonomy extraction, and FastAPI endpoint routes.

```bash
# Run full backend pytest suite
pytest backend/tests -v

# Run performance and latency benchmark suite
pytest backend/tests/test_performance_benchmarks.py -v

# Run Top 9 architectural integrity suite
pytest backend/tests/test_top9_integrity.py -v

# Verify frontend production build
cd frontend
npm run build
```

---

## 🌟 9-Pillar Architecture & Quality Checklist

Every major feature or Pull Request must adhere to the 9 Core Architectural Standards:

1. **Async Non-Blocking I/O**: Endpoints must leverage `async def` and preserve sub-1.5s response SLAs.
2. **Deterministic 4-Pillar Scoring**: Compliance calculations must be mathematically grounded and auditable.
3. **BM25+ Keyword Retrieval**: Search recall must penalize keyword stuffing via asymptotic term saturation.
4. **Layout Linearization**: Ensure multi-column documents clear the $\ge 12\text{pt}$ gutter threshold.
5. **ISO 19005-2 Font Integrity**: Normalize typographic ligatures and strip PUA glyphs into clean ASCII.
6. **Timeline Normalization**: Standardize employment dates to ISO months and detect $>90$-day gaps.
7. **EEOC / NYC LL 144 Anonymization**: Protect candidate privacy by removing all PII before blind audits.
8. **Ontological Skill Taxonomy**: Enforce a Hard-to-Soft skill ratio $R_{\text{skill}} \ge 0.70$.
9. **Single-Column Resume Compilation**: PDF builders must produce strict single-column ATS layouts.

---

## 📋 Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(...)`: A new user-facing feature or API endpoint
- `fix(...)`: A bug fix
- `perf(...)`: Performance and latency optimizations
- `docs(...)`: Documentation updates or additions
- `test(...)`: Adding or updating test cases and benchmarks
- `refactor(...)`: Code changes that neither fix bugs nor add features
- `ci(...)`: Changes to CI/CD workflows and automated pipelines
- `chore(...)`: Maintenance tasks, dependency updates, configuration tweaks

---

## 🔒 Security & Performance Guidelines

- Never hardcode or commit API secrets or keys. Use `.env` files (ignored in `.gitignore`).
- Enforce strict input sanitization and payload limits on document parsers (`pypdf`, `python-docx`).
- Ensure all API endpoints include security and latency headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).
- Keep all deterministic text processing operations under 25ms per execution.
