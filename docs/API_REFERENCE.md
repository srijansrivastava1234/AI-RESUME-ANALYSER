# AI Resume Analyser - Complete API Reference

Welcome to the **AI Resume Analyser API** documentation. The backend is built with FastAPI, executing deterministic Applicant Tracking System (ATS) audit pipelines, multi-engine simulation sandboxes, and LLM-assisted career intelligence in sub-millisecond to sub-10ms response times.

---

## Base URL
```
http://localhost:8000
```
Interactive Swagger UI: `http://localhost:8000/docs`  
ReDoc Documentation: `http://localhost:8000/redoc`

---

## Authentication & Security
- **Rate Limiting**: 10 analysis requests / minute per IP (enforced via SlowAPI).
- **SSRF Protection**: All URL scraping endpoints strictly reject private RFC 1918 subnets, loopbacks (`127.0.0.1`), and link-local addresses.
- **Request Tracing**: Every response includes `X-Request-ID` and `X-Process-Time` timing headers.

---

## Endpoint Catalog

### 1. System Health & Diagnostics

#### `GET /api/health`
Returns service uptime, semantic version, and supported file ingestion formats.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "3.2.0",
  "service": "AI Resume Analyser API",
  "supported_formats": ["pdf", "docx", "txt"],
  "max_file_size_mb": 10
}
```

#### `GET /api/diagnostics`
Returns runtime environment status, loaded ATS simulators, and active regulatory compliance rules.

---

### 2. Core ATS Analysis

#### `POST /api/analyze`
Accepts a single resume file (`.pdf`, `.docx`, `.txt`) and optional job description for full composite evaluation.

**Parameters (multipart/form-data)**:
- `file` (UploadFile, required): Target resume file (max 10MB).
- `job_description` (string, optional): Target job posting text.

**Response `200 OK`**:
```json
{
  "filename": "alex_mercer_resume.pdf",
  "char_count": 2840,
  "report": {
    "ats_score": 92,
    "metrics": [
      { "name": "Google/IBM XYZ Impact", "score": 95, "feedback": "Excellent quantification." },
      { "name": "BM25+ Lexical Match", "score": 88, "feedback": "Strong keyword overlap." }
    ],
    "key_strengths": ["Strong action verbs", "Clean single-column layout"],
    "improvements": []
  }
}
```

---

### 3. Multi-ATS Engine Simulation & Sandboxing

#### `POST /api/simulate/ats`
Emulates parsing across Workday, Greenhouse/Lever, Taleo/Oracle, and iCIMS Enterprise sandbox engines.

**Request Payload**:
```json
{
  "resume_text": "Alex Mercer\nPrincipal Cloud Architect\n• Architected cross-region Kubernetes..."
}
```

**Response `200 OK`**:
```json
{
  "overall_cross_ats_score": 92,
  "tier": "Universal ATS Compatible (Low Risk)",
  "engines": {
    "workday": { "engine": "Workday", "compatibility_score": 95, "hazards": [] },
    "greenhouse": { "engine": "Greenhouse / Lever", "compatibility_score": 92, "hazards": [] },
    "taleo": { "engine": "Taleo / Oracle", "compatibility_score": 88, "hazards": [] },
    "icims": { "engine": "iCIMS Enterprise", "compatibility_score": 94, "hazards": [] }
  },
  "summary_alerts": []
}
```

#### Individual Dedicated Simulator Endpoints:
- `POST /api/simulate/icims`: Deep diagnostic parsing audit for iCIMS Enterprise Talent Cloud.
- `POST /api/simulate/workday`: Workday parsing and section schema verification.
- `POST /api/simulate/greenhouse`: Greenhouse and Lever token stream and skill cluster density analyzer.
- `POST /api/simulate/taleo`: Taleo legacy table flattening and chronological date validator.

---

### 4. Job Description URL Scraper

#### `POST /api/scrape-jd`
Fetches and sanitizes job descriptions from live URLs (Greenhouse, Lever, LinkedIn, Indeed, SmartRecruiters, Jobvite).

**Request Payload**:
```json
{
  "url": "https://boards.greenhouse.io/example/jobs/12345"
}
```

---

### 5. Recruiter "Grill-Me" Interview Prep

#### `POST /api/interview-prep`
Generates targeted behavioral and technical challenge questions based on identified resume gaps.

---

### 6. Cover Letter & Outreach Studio

#### `POST /api/generate-outreach`
Generates tailored cover letters, recruiter LinkedIn InMails, hiring manager cold emails, and follow-up notes.

**Modes**:
- `cover_letter` (200 words, XYZ accomplishment-driven)
- `linkedin_inmail` (80 words, high-conversion recruiter hook)
- `hiring_manager_email` (Direct cold email with tailored subject line)
- `follow_up` (Post-interview or post-application note)

---

### 7. Security, Typographic & Schema Exporter Specifications

- **Homoglyph Attack Defense**: Mixed-script Cyrillic/Greek lookalike character injection detection (`app.hack_detector`).
- **URL & Domain Security**: Automated detection of URL shorteners (bit.ly, t.co) and raw numeric IP addresses (`app.portfolio_validator`).
- **Typography & Glyph Fidelity**: Non-standard emoji/dingbat bullet sanitization and period consistency checking (`app.bullet_linter`).
- **JSON Resume Standard Exporter**: Serialization to official v1.0.0 JSON Resume schema specification (`app.schema_exporter`).
- **CLI Diagnostics**: Run `python backend/app/cli.py resume.pdf --simulate` for interactive multi-ATS terminal matrix outputs.
