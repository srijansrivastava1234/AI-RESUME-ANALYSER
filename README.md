# AI Resume Analyser

A visually premium, modern ATS (Applicant Tracking System) compiler and resume auditing dashboard. It analyzes resume PDFs and compares them against target job descriptions using Gemini AI to score and suggest actionable enhancements.

## 🛠️ Architecture

- **Backend:** FastAPI (Python 3.10+) utilizing Uvicorn, PyPDF for text extraction, and the Google Generative AI SDK for Gemini models.
- **Frontend:** React 19 + Vite 8, styled with raw CSS (glassmorphism design system) and powered by Lucide icons.

## 📂 Project Structure

```
AI-RESUME-ANALYSER/
├── backend/            # FastAPI API server
│   ├── app/            # App endpoints, parsing, and analyzer modules
│   └── .env.example    # Backend env template
├── frontend/           # Vite + React Dashboard
│   ├── src/            # Components, styles, and dashboard layout
│   └── package.json    # Frontend dependencies
└── README.md           # Main documentation
```

## ⚙️ Quick Start Setup

### 1. Prerequisites
- Python 3.10+
- Node.js (LTS version)

### 2. Configure Backend API
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create your virtual environment and activate it:
   ```bash
   python -m venv .venv
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and set your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your `GEMINI_API_KEY`. Get a key from [Google AI Studio](https://aistudio.google.com/).

5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will run on `http://127.0.0.1:8000`.

### 3. Run Frontend Dashboard
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   The dashboard UI will run on `http://localhost:5173`.
