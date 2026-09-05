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

## 🧪 Running Automated Tests

We maintain comprehensive automated test suites for document parsing, heuristic scoring, keyword taxonomy extraction, and FastAPI endpoint routes.

```bash
# Run backend pytest suite from repository root
pytest backend/tests -v

# Verify frontend production build
cd frontend
npm run build
```

---

## 📋 Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(...)`: A new user-facing feature or API endpoint
- `fix(...)`: A bug fix
- `docs(...)`: Documentation updates or additions
- `test(...)`: Adding or updating test cases
- `refactor(...)`: Code changes that neither fix bugs nor add features
- `ci(...)`: Changes to CI/CD workflows and automated pipelines
- `chore(...)`: Maintenance tasks, dependency updates, configuration tweaks

---

## 🔒 Security & Performance Guidelines

- Never hardcode or commit API secrets or keys. Use `.env` files (ignored in `.gitignore`).
- Enforce strict input sanitization and payload limits on document parsers (`pypdf`, `python-docx`).
- Ensure all API endpoints include security and latency headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).
