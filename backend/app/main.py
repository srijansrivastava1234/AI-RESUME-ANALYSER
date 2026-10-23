import os
# Force pure-python protobuf implementation to support Python 3.14+ pre-releases
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from app.limiter import limiter
from app.logging_config import setup_logging, generate_request_id
from app.schemas import *  # Re-export all schemas for complete backward compatibility

# Modular APIRouters
from app.routers.analysis import router as analysis_router, MAX_FILE_SIZE_BYTES, MAX_COMPARE_FILES
from app.routers.bullets import router as bullets_router
from app.routers.audits import router as audits_router
from app.routers.simulators import router as simulators_router
from app.routers.compliance import router as compliance_router
from app.routers.tools import router as tools_router

# Load environmental variables from .env if present
load_dotenv()

APP_VERSION = "3.7.0"

# Initialize structured JSON logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("ResumeAnalyserAPI")

app = FastAPI(
    title="AI Resume Analyser API",
    description=(
        "Enterprise-grade, modular REST API for resume ingestion, 4-pillar deterministic "
        "ATS compliance scoring, and generative AI feedback. Grounded in the 10 Core Architectural Pillars."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Attach rate limiter state to the app
app.state.limiter = limiter

# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. You are rate-limited to 10 analysis requests per minute. Please wait before retrying.",
            "retry_after_seconds": 60
        }
    )

# Custom performance, security, and request tracing headers middleware
@app.middleware("http")
async def add_process_time_and_security_headers(request: Request, call_next):
    request_id = generate_request_id()
    start_time = time.time()

    # Attach request_id to request state for downstream access
    request.state.request_id = request_id

    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Client: {get_remote_address(request)}"
    )

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    logger.info(
        f"[{request_id}] Response {response.status_code} in {process_time:.4f}s"
    )

    return response

# Configure CORS: If wildcard origins are used, credentials must be disabled per W3C spec
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if allowed_origins_env and allowed_origins_env != "*":
    allow_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
    allow_credentials = True
else:
    allow_origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular routers
app.include_router(analysis_router)
app.include_router(bullets_router)
app.include_router(audits_router)
app.include_router(simulators_router)
app.include_router(compliance_router)
app.include_router(tools_router)

# Mount static frontend build if present (for production Docker or unified deployments)
frontend_dist_paths = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")),
    "/app/frontend/dist",
    os.path.abspath("frontend/dist"),
]

frontend_dist_dir = next((p for p in frontend_dist_paths if os.path.isdir(p)), None)

if frontend_dist_dir:
    assets_dir = os.path.join(frontend_dist_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")
    app.mount("/dashboard", StaticFiles(directory=frontend_dist_dir, html=True), name="frontend-dashboard")


@app.get("/")
def read_root(request: Request):
    # If a browser requests the root directly in production and frontend build exists, serve it
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header and frontend_dist_dir:
        index_file = os.path.join(frontend_dist_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)

    return {
        "status": "Online",
        "version": APP_VERSION,
        "service": "AI Resume Analyser Service",
        "endpoints": {
            "/api/analyze": "POST - Upload PDF/DOCX/TXT resume and optional job description to get ATS analysis",
            "/api/compare": "POST - Upload multiple resumes for side-by-side ATS ranking",
            "/api/hygiene": "POST - Evaluate ATS formatting hygiene, contact completeness, and section headers",
            "/api/score-bullet": "POST - Deterministic Google/IBM XYZ mathematical bullet impact evaluation",
            "/api/optimize-bullet": "POST - Optimize single resume bullet point into XYZ format",
            "/api/compliance-audit": "POST - Deterministic 4-Pillar ATS Compliance Audit & Regulatory Safe Harbor check",
            "/api/agent-prompt": "POST - Synthesize Agent-Native BYOK refactoring prompt for external LLMs",
            "/api/health": "GET - Service health check"
        }
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint for uptime monitoring and deployment readiness."""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "service": "AI Resume Analyser API",
        "supported_formats": ["pdf", "docx", "txt"],
        "max_file_size_mb": MAX_FILE_SIZE_BYTES // (1024 * 1024)
    }


@app.get("/api/diagnostics")
def get_diagnostics():
    """
    Returns runtime diagnostics, loaded ATS simulation engines,
    deterministic scoring modules, and security policies.
    """
    return {
        "status": "operational",
        "version": APP_VERSION,
        "environment": {
            "pure_python_protobuf": os.environ.get("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION") == "python",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
            "max_compare_files": MAX_COMPARE_FILES,
        },
        "engines": {
            "ats_simulators": ["workday", "greenhouse", "taleo"],
            "scoring_pillars": [
                "deterministic_bm25_plus",
                "font_cmap_integrity",
                "career_chronology",
                "viewport_first_third",
                "token_density",
                "google_ibm_xyz_scorer",
                "adverse_impact_four_fifths",
                "blind_pii_redactor",
                "ats_hack_detector",
                "layout_linearizer_xy_cut"
            ],
            "ai_integration": {
                "gemini_enabled": bool(os.getenv("GEMINI_API_KEY")),
                "deterministic_fallback_ready": True
            }
        },
        "compliance": {
            "nyc_local_law_144": "enforced",
            "eeoc_four_fifths_rule": "active",
            "eu_ai_act_article_10": "compliant"
        }
    }
