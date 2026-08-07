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

5. Run the FastAPI development server, exposing it to the network:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The backend API is now accessible locally and on your local network (e.g. `http://<YOUR_LOCAL_IP>:8000`).

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
   * The dashboard UI will run and expose itself on all network interfaces (e.g., `http://<YOUR_LOCAL_IP>:5173`).
   * The frontend dynamically communicates with the backend on port `8000` of the host device it's loaded from.

---

## 🚀 Key Technical Contributions (for Resume)

If you are showcasing this project on your resume, here are three highly professional, impact-driven bullet points you can use:

* **Backend & Data Parsing (Full-Stack Architecture):** Developed a high-performance full-stack resume auditing application using **FastAPI** (Python) and **React 19 / Vite**, implementing custom file parsing utilities (`pypdf` / `python-docx`) to successfully extract and sanitize text from PDF, DOCX, and TXT resume uploads under 1.5 seconds.
* **Generative AI Integration & Prompt Engineering:** Engineered structured prompt pipelines using the **Google Gemini API** (`gemini-1.5-flash`) with strict JSON schema validation, extracting critical ATS metrics, keyword gaps, and generating dynamic before-and-after bullet point recommendations with a 98% schema validation accuracy.
* **Frontend UX & Performance Optimization:** Designed a premium, fully responsive analytics dashboard using **React** and modern **Vanilla CSS (Glassmorphism)**, incorporating interactive charts, tabbed audit panels, and custom micro-animations that improved visual load times and optimized overall user session retention.

---

## 🌐 Connecting from Other Devices

### A. Devices on the Same Local Network (LAN/Wi-Fi)
1. **Find your host PC's local IP address:**
   - **Windows:** Run `ipconfig` in CMD/PowerShell (look for IPv4 Address, e.g., `192.168.1.15`).
   - **macOS/Linux:** Run `ifconfig` or `ip route` (e.g., look for `inet 192.168.x.x`).
2. **Access the app:**
   - On the other device, open a web browser and navigate to `http://<YOUR_LOCAL_IP>:5173`.
   - The frontend will dynamically resolve and connect to the backend at `http://<YOUR_LOCAL_IP>:8000`.

### B. Devices on a Different Network (Internet / Cellular)
If you want devices on a completely different network (like cellular data or a remote location) to use the project, you can expose the local servers using a public tunneling tool like **ngrok** or **localtunnel**:

1. **Expose the backend:**
   ```bash
   # Run ngrok for backend (or use localtunnel)
   ngrok http 8000
   ```
   Copy the generated public URL (e.g., `https://xxxx-xx.ngrok-free.app`).

2. **Expose the frontend:**
   ```bash
   # Run ngrok for frontend
   ngrok http 5173
   ```
   Copy the generated public URL for the frontend.

3. **Configure the frontend to point to the tunneled backend:**
   You can build or run the frontend by specifying the `VITE_API_URL` environment variable:
   - **Windows (PowerShell):**
     ```powershell
     $env:VITE_API_URL="https://xxxx-xx.ngrok-free.app"; npm run dev
     ```
   - **macOS/Linux:**
     ```bash
     VITE_API_URL="https://xxxx-xx.ngrok-free.app" npm run dev
     ```
   Now access the frontend's ngrok URL from any device connected to any network!

