import pytest
from app.portfolio_validator import audit_portfolio_links


def test_empty_portfolio_links():
    res = audit_portfolio_links("")
    assert res["links_found"] == 0
    assert res["link_score"] == 0.0
    assert res["status"] == "PASS"


def test_perfect_portfolio_links():
    text = (
        "Email: alex@example.com | LinkedIn: https://linkedin.com/in/alexsmith-eng | "
        "GitHub: https://github.com/alexsmith | Portfolio: https://alexsmith.dev"
    )
    res = audit_portfolio_links(text)
    assert res["links_found"] >= 3
    assert res["has_linkedin"] is True
    assert res["has_github"] is True
    assert res["has_portfolio"] is True
    assert res["link_score"] >= 90.0
    assert res["status"] == "EXCELLENT"


def test_placeholder_and_insecure_links():
    text = "GitHub: http://github.com/your-username | LinkedIn: http://linkedin.com/in/username"
    res = audit_portfolio_links(text)
    assert res["has_github"] is True
    assert res["status"] == "CRITICAL"
    assert any(link["is_placeholder"] for link in res["links"])
    assert any("placeholder" in f.lower() for f in res["feedback"])
