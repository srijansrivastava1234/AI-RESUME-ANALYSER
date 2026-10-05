import pytest
from backend.app.simulators.successfactors import simulate_successfactors_parsing

def test_simulate_successfactors_empty():
    res = simulate_successfactors_parsing("")
    assert res["compatibility_score"] == 0
    assert res["is_safe"] is False
    assert "Empty document provided." in res["hazards"]

def test_simulate_successfactors_compliant_resume():
    text = """
    Alice Johnson
    Email: alice.j@company.org
    Phone: (555) 987-6543
    
    Professional Experience
    Lead DevOps Engineer, Enterprise Corp (2018 - Present)
    • Managed multi-region Kubernetes clusters on AWS and Google Cloud.
    • Architected zero-downtime CI/CD deployment pipelines using GitLab CI.
    
    Software Engineer, Startup Inc (2015 - 2018)
    • Developed microservices in Python and Go with PostgreSQL.
    
    Education
    Bachelor of Science in Computer Science, State University (2011 - 2015)
    
    Technical Skills
    Kubernetes, Docker, AWS, GCP, Python, Go, CI/CD, Terraform
    
    Certifications
    AWS Certified Solutions Architect Professional
    """
    res = simulate_successfactors_parsing(text)
    assert res["engine"] == "SAP SuccessFactors"
    assert res["compatibility_score"] >= 80
    assert res["is_safe"] is True
    assert res["extracted_fields"]["has_contact_data"] is True
    assert "bachelor" in res["extracted_fields"]["degrees_identified"]
    assert res["extracted_fields"]["employment_periods_count"] >= 2
    assert len(res["hazards"]) == 0

def test_simulate_successfactors_missing_sections_and_tables():
    text = """
    Random Notes
    +++++++
    | Col1 | Col2 |
    +++++++
    I worked at some place for a while.
    """
    res = simulate_successfactors_parsing(text)
    assert res["compatibility_score"] < 60
    assert res["is_safe"] is False
    assert any("Missing standard SuccessFactors section header" in h for h in res["hazards"])
    assert any("Complex tabular" in h for h in res["hazards"])
