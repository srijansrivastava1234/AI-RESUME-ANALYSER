import pytest
from app.bullet_length import analyze_bullet_lengths


def test_empty_bullets():
    res = analyze_bullet_lengths("")
    assert res["total_bullets"] == 0
    assert res["scannability_score"] == 0.0
    assert res["status"] == "PASS"


def test_optimal_bullet_distribution():
    text = """
    • Architected high-throughput microservices using FastAPI, Docker, and PostgreSQL, increasing system reliability by 35% across four cloud regions.
    • Spearheaded transition from legacy monolithic codebase to event-driven Kafka messaging, reducing backend data processing latency by 45 milliseconds.
    • Directed cross-functional engineering team of eight developers to deliver enterprise analytics features on time and under budget.
    """
    res = analyze_bullet_lengths(text)
    assert res["total_bullets"] == 3
    assert res["optimal_count"] >= 2
    assert res["scannability_score"] >= 80.0
    assert res["status"] == "EXCELLENT"


def test_stubs_and_run_ons():
    text = """
    • Fixed bugs.
    • Did coding.
    • Designed, implemented, maintained, refactored, coordinated, deployed, configured, integrated, tested, monitored, optimized, documented, managed, and reviewed over four hundred separate distributed asynchronous multi-threaded cloud-native microservices across seventy-two distinct production data centers without incurring a single second of unplanned downtime or service disruption over seven consecutive fiscal years.
    """
    res = analyze_bullet_lengths(text)
    assert res["stubs_count"] >= 2
    assert res["run_on_count"] >= 1
    assert res["scannability_score"] < 70.0
    assert len(res["flagged_bullets"]) >= 2
