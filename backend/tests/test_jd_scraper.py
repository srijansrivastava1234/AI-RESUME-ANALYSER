import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.jd_scraper import (
    validate_url_security,
    clean_job_text,
    extract_skills_from_text,
    parse_job_html,
    scrape_job_description
)

client = TestClient(app)

def test_validate_url_security_ssrf_blocking():
    # Loopback / Localhost
    with pytest.raises(ValueError, match="prohibited|blocked|restricted"):
        validate_url_security("http://localhost:8000/internal")

    with pytest.raises(ValueError, match="prohibited|blocked|restricted"):
        validate_url_security("http://127.0.0.1:3000")

    with pytest.raises(ValueError, match="prohibited|blocked|restricted"):
        validate_url_security("http://0.0.0.0")

    # Invalid scheme
    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        validate_url_security("ftp://ftp.example.com/file")

    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        validate_url_security("file:///etc/passwd")

    # Empty
    with pytest.raises(ValueError, match="Invalid target URL"):
        validate_url_security("")


def test_clean_job_text_strips_boilerplate():
    raw = """
    Senior Python Developer needed.
    Requirements:
    - 5+ years experience in Python, FastAPI, and Kubernetes.
    - Strong communication skills.
    
    Equal Opportunity Employer Statement: We are an equal opportunity employer and do not discriminate on the basis of race, color, or gender.
    All qualified applicants will receive consideration for employment without regard to race.
    We use cookies to enhance your browsing experience.
    """
    cleaned = clean_job_text(raw)
    assert "Senior Python Developer" in cleaned
    assert "FastAPI" in cleaned
    assert "Equal Opportunity Employer" not in cleaned
    assert "cookies" not in cleaned


def test_extract_skills_from_text():
    text = "We are hiring a backend engineer skilled in Python, FastAPI, Docker, and AWS. Knowledge of React and PostgreSQL is a plus."
    skills = extract_skills_from_text(text)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills
    assert "AWS" in skills
    assert "React" in skills
    assert "PostgreSQL" in skills
    assert "Go" not in skills  # Should not false match random letters


def test_parse_job_html_greenhouse():
    html = """
    <html>
      <head><title>Backend Engineer at Acme</title></head>
      <body>
        <div class="app-title">Backend Engineer</div>
        <div class="company-name">Acme Inc.</div>
        <div id="content">
          <p>We are looking for a Backend Engineer with experience in Python and PostgreSQL.</p>
          <p>Responsibilities include building scalable REST APIs and maintaining Kubernetes infrastructure.</p>
        </div>
      </body>
    </html>
    """
    result = parse_job_html(html, "https://boards.greenhouse.io/acme/jobs/12345")
    assert result["success"] is True
    assert result["job_title"] == "Backend Engineer"
    assert result["company"] == "Acme Inc."
    assert "Python" in result["extracted_skills"]
    assert "PostgreSQL" in result["extracted_skills"]
    assert "Kubernetes" in result["extracted_skills"]
    assert result["word_count"] > 10


def test_parse_job_html_lever():
    html = """
    <html>
      <body>
        <h2 class="posting-headline">Staff Platform Engineer</h2>
        <div class="posting-description">
          <h3>About the role</h3>
          <p>Lead our cloud infrastructure modernization on AWS using Terraform and Docker.</p>
        </div>
      </body>
    </html>
    """
    result = parse_job_html(html, "https://jobs.lever.co/techcorp/67890")
    assert result["success"] is True
    assert result["job_title"] == "Staff Platform Engineer"
    assert "AWS" in result["extracted_skills"]
    assert "Terraform" in result["extracted_skills"]
    assert "Docker" in result["extracted_skills"]


def test_parse_job_html_ashby():
    html = """
    <html>
      <body>
        <h1>Lead Security Engineer</h1>
        <div data-qa="job-description">
          <p>We are seeking a Lead Security Engineer with expertise in OAuth, JWT, Prometheus, and Linux.</p>
        </div>
      </body>
    </html>
    """
    result = parse_job_html(html, "https://jobs.ashbyhq.com/cyber/55555")
    assert result["success"] is True
    assert result["job_title"] == "Lead Security Engineer"
    assert "OAuth" in result["extracted_skills"]
    assert "Linux" in result["extracted_skills"]


def test_parse_job_html_generic():
    html = """
    <html>
      <head><title>Full Stack Developer at Startup</title></head>
      <body>
        <main>
          <h1>Full Stack Developer</h1>
          <p>Join our team building web apps with TypeScript, React, and Node.js.</p>
          <p>Deploy microservices to AWS using Docker and CI/CD pipelines.</p>
        </main>
      </body>
    </html>
    """
    result = parse_job_html(html, "https://careers.startup.io/dev")
    assert result["success"] is True
    assert "TypeScript" in result["extracted_skills"]
    assert "React" in result["extracted_skills"]


def test_api_scrape_jd_endpoint_ssrf_error():
    response = client.post(
        "/api/scrape-jd",
        json={"url": "http://127.0.0.1:8000/private"}
    )
    assert response.status_code == 400
    assert "prohibited" in response.json()["detail"] or "blocked" in response.json()["detail"]


def test_api_scrape_jd_endpoint_success():
    import asyncio
    sample_html = """
    <html>
      <head><title>Full Stack Developer - CloudSoft</title></head>
      <body>
        <h1>Full Stack Developer</h1>
        <main>
          <p>Join CloudSoft as a Full Stack Developer working with TypeScript, React, and Node.js.</p>
          <p>Deploy microservices to AWS using Docker and CI/CD pipelines.</p>
        </main>
      </body>
    </html>
    """
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = sample_html

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with patch("app.jd_scraper.validate_url_security"):
            res = asyncio.run(scrape_job_description("https://cloudsoft.example.com/careers/fullstack"))
            assert res["success"] is True
            assert res["job_title"] == "Full Stack Developer"
            assert "TypeScript" in res["extracted_skills"]
            assert "React" in res["extracted_skills"]

