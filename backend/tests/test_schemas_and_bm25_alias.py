import pytest
from pydantic import ValidationError
import app.bm25 as bm25_alias
from app.bm25_scorer import compute_bm25_plus, tokenize, calculate_idf
from app.schemas import (
    OptimizeBulletPayload,
    ScoreBulletPayload,
    ComplianceAuditPayload,
    ScrapeJdPayload,
    SimulateAtsPayload,
    InterviewPrepPayload,
    GenerateOutreachPayload,
    HealthResponse,
    DiagnosticsResponse
)

def test_bm25_backward_compatibility_alias():
    assert bm25_alias.tokenize == tokenize
    assert bm25_alias.calculate_idf == calculate_idf
    assert bm25_alias.compute_bm25_plus == compute_bm25_plus
    assert bm25_alias.calculate_bm25_score == compute_bm25_plus
    assert bm25_alias.DEFAULT_K1 == 1.2
    assert bm25_alias.DEFAULT_B == 0.75
    assert bm25_alias.DEFAULT_DELTA == 1.0

    doc = "Experienced Python developer working with AWS and Docker containers"
    keywords = ["python", "aws", "docker"]
    score = bm25_alias.calculate_bm25_score(doc, keywords)
    assert score["raw_bm25_score"] > 0
    assert score["normalized_score"] > 0
    assert score["matched_keywords"] == 3

def test_pydantic_schemas_valid():
    opt = OptimizeBulletPayload(bullet="Built microservices in Go", target_role="Backend Engineer")
    assert opt.bullet == "Built microservices in Go"

    score_p = ScoreBulletPayload(bullet="Developed FastAPI backend", seniority="senior")
    assert score_p.seniority == "senior"

    comp = ComplianceAuditPayload(resume_text="Experienced engineer with 10 years experience", seniority="lead", target_pages=2)
    assert comp.target_pages == 2

    scrape = ScrapeJdPayload(url="https://jobs.example.com/posting/123")
    assert scrape.url.startswith("https://")

    sim = SimulateAtsPayload(resume_text="Jane Doe Senior Architect Experience...")
    assert len(sim.resume_text) >= 10

    prep = InterviewPrepPayload(resume_text="Jane Doe Senior Architect Experience...", target_role="Lead Architect")
    assert prep.target_role == "Lead Architect"

    outreach = GenerateOutreachPayload(resume_text="Jane Doe Senior Architect Experience...", outreach_type="cover_letter")
    assert outreach.outreach_type == "cover_letter"

    health = HealthResponse(version="3.7.0")
    assert health.status == "healthy"
    assert health.version == "3.7.0"

    diag = DiagnosticsResponse(
        status="operational",
        version="3.7.0",
        environment={"python": "3.11"},
        engines={"bm25": "ready"},
        compliance={"EEOC": "active"}
    )
    assert diag.status == "operational"

def test_pydantic_schemas_invalid():
    with pytest.raises(ValidationError):
        OptimizeBulletPayload(bullet="too")  # min_length is 5

    with pytest.raises(ValidationError):
        SimulateAtsPayload(resume_text="short")  # min_length is 10
