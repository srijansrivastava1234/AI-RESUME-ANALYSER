import pytest
from app.metric_validator import audit_bullet_metrics


def test_business_outcome_revenue_and_percentage():
    bullet = "Engineered automated checkout pipeline generating $2.4M in annual revenue with a 35% conversion lift."
    result = audit_bullet_metrics(bullet)
    assert result["has_business_outcome"] is True
    assert result["has_vanity_metric"] is False
    assert result["vanity_penalty"] == 0
    assert result["metric_type"] == "business_outcome"
    assert len(result["detected_outcomes"]) >= 2


def test_business_outcome_latency_and_scale():
    bullet = "Optimized Redis caching tier reducing P99 query latency to 120ms across 10M MAU."
    result = audit_bullet_metrics(bullet)
    assert result["has_business_outcome"] is True
    assert result["metric_type"] == "business_outcome"
    assert result["vanity_penalty"] == 0


def test_vanity_metric_loc():
    bullet = "Wrote 10,000 lines of code in Python for internal reporting tools."
    result = audit_bullet_metrics(bullet)
    assert result["has_vanity_metric"] is True
    assert result["has_business_outcome"] is False
    assert result["vanity_penalty"] == 20
    assert result["metric_type"] == "vanity_activity"
    assert "Replace arbitrary task counts" in result["feedback"]


def test_vanity_metric_meetings():
    bullet = "Attended 50 meetings with stakeholders to discuss product roadmap."
    result = audit_bullet_metrics(bullet)
    assert result["has_vanity_metric"] is True
    assert result["vanity_penalty"] == 20


def test_vanity_metric_tickets():
    bullet = "Closed 300 tickets in Jira backlog over the quarter."
    result = audit_bullet_metrics(bullet)
    assert result["has_vanity_metric"] is True
    assert result["vanity_penalty"] == 20


def test_false_positive_versions_and_ports():
    bullet = "Upgraded production services from Python 3.9 to Python 3.12 and exposed Port 8080."
    result = audit_bullet_metrics(bullet)
    assert result["has_business_outcome"] is False
    assert result["has_vanity_metric"] is False
    assert len(result["detected_false_positives"]) >= 2
    assert result["metric_type"] == "false_positive"


def test_empty_bullet():
    result = audit_bullet_metrics("")
    assert result["has_metric"] is False
    assert result["metric_type"] == "none"
    assert result["vanity_penalty"] == 0
