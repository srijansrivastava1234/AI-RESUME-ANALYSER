import pytest
from app.layout_linearizer import simulate_recursive_xy_cut

def test_empty_and_whitespace_input():
    empty_res = simulate_recursive_xy_cut("")
    assert empty_res["linearization_score"] == 0
    assert empty_res["risk_tier"] == "Empty Document"
    assert not empty_res["is_linear_safe"]

    ws_res = simulate_recursive_xy_cut("   \n\t\n   ")
    assert ws_res["linearization_score"] == 0
    assert ws_res["risk_tier"] == "Empty Document"

def test_clean_single_column_layout():
    single_column = (
        "Jane Doe\n"
        "Senior Cloud Architect\n"
        "Work Experience\n"
        "Acme Corp - Lead Infrastructure Engineer\n"
        "- Architected multi-region Kubernetes clusters scaling to 500k RPS with zero downtime.\n"
        "- Automated CI/CD deployment pipelines cutting release turnaround from 4 hours to 12 minutes.\n"
        "Education\n"
        "B.S. in Computer Science, Stanford University\n"
        "Skills\n"
        "Go, Python, Terraform, Docker, Kubernetes, AWS\n"
    )
    res = simulate_recursive_xy_cut(single_column)
    assert res["linearization_score"] >= 85
    assert res["risk_tier"] == "Safe Single-Column"
    assert res["is_linear_safe"] is True
    assert res["gutter_anomaly_count"] == 0
    assert res["interleaving_hazard_count"] == 0
    assert len(res["simulated_scrambled_snippets"]) == 0
    assert "Clean single-column layout verified" in res["recommendations"][0]

def test_severe_multi_column_sidebar_scrambling():
    # Multi-column text with >= 4 spaces separating left sidebar from right column
    multi_column = (
        "Skills: Python, Go        Acme Corp - Lead Engineer\n"
        "Tools: Docker, K8s        Architected multi-region cloud cluster\n"
        "Contact: jane@test.com    Decreased API latency by 45% using Redis\n"
        "Education: BS CS 2020     Mentored 8 junior and mid-level developers\n"
        "Languages: English        Managed $1.2M annual AWS cloud infrastructure\n"
    )
    res = simulate_recursive_xy_cut(multi_column)
    assert res["linearization_score"] < 60
    assert res["risk_tier"] == "Critical Layout Collapse"
    assert res["is_linear_safe"] is False
    assert res["gutter_anomaly_count"] >= 4
    assert res["interleaving_hazard_count"] >= 3
    assert len(res["simulated_scrambled_snippets"]) > 0
    assert any("Skills: Python, Go Acme Corp - Lead Engineer" in s for s in res["simulated_scrambled_snippets"])

def test_moderate_multi_column_risk():
    mixed_doc = (
        "John Doe\n"
        "Software Engineer\n"
        "Experience\n"
        "Senior Developer at ScaleFlow\n"
        "- Built microservices handling 10k RPS.\n"
        "Skills: React, Node        Jan 2022 - Present\n"
        "Tools: Git, Docker         San Francisco, CA\n"
        "Hobbies: Hiking, Chess\n"
        "Education: State University\n"
        "Certifications: AWS SAA\n"
    )
    res = simulate_recursive_xy_cut(mixed_doc)
    assert 60 <= res["linearization_score"] < 85
    assert res["risk_tier"] == "Moderate Multi-Column Risk"
    assert res["gutter_anomaly_count"] >= 2

def test_ascii_table_divider_penalties():
    table_doc = (
        "+-------------------------------------------------------------+\n"
        "| Jane Doe | Cloud Engineer                                  |\n"
        "+-------------------------------------------------------------+\n"
        "| Experience                                                  |\n"
        "+-------------------------------------------------------------+\n"
        "| Acme Corp - Architected cloud pipelines                    |\n"
        "+-------------------------------------------------------------+\n"
        "| Skills                                                      |\n"
        "+-------------------------------------------------------------+\n"
        "===============================================================\n"
    )
    res = simulate_recursive_xy_cut(table_doc)
    assert res["table_divider_count"] >= 5
    assert any("ASCII table" in rec for rec in res["recommendations"])

def test_tab_separated_columns():
    tab_doc = (
        "Skills:\t\tSenior Engineer at TechCo\n"
        "Kubernetes\t\tOptimized container networking and service mesh\n"
    )
    res = simulate_recursive_xy_cut(tab_doc)
    assert res["gutter_anomaly_count"] >= 1
    assert res["interleaving_hazard_count"] >= 1

def test_minor_divider_lines():
    doc = (
        "Jane Doe\n"
        "--------------------\n"
        "Software Engineer\n"
        "====================\n"
        "Built cloud microservices\n"
    )
    res = simulate_recursive_xy_cut(doc)
    assert res["table_divider_count"] == 2
    assert any("Consider replacing graphic ASCII divider lines" in rec for rec in res["recommendations"])

def test_only_blank_lines():
    res = simulate_recursive_xy_cut("\n\n\n\n")
    assert res["linearization_score"] == 0
    assert res["total_analyzed_lines"] == 0

