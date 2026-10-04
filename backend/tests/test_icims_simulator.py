import pytest
from app.simulators.icims import simulate_icims_parsing
from app.ats_simulator import run_multi_ats_simulation

def test_icims_simulator_empty_text():
    res = simulate_icims_parsing("")
    assert res["compatibility_score"] == 0
    assert res["is_safe"] is False
    assert "Empty document" in res["hazards"][0]

def test_icims_simulator_clean_resume():
    text = """
    Jane Doe
    jane.doe@example.com | (555) 123-4567 | linkedin.com/in/janedoe

    Summary
    Senior Python and Cloud Developer with 7+ years of experience.

    Work Experience
    Lead Software Engineer - Acme Corp
    Jan 2020 - Present
    - Architected scalable microservices using FastAPI and AWS.
    - Improved throughput by 40%.

    Education
    Bachelor of Science in Computer Science - State University
    2015 - 2019

    Skills
    Python, FastAPI, AWS, Docker, PostgreSQL
    """
    res = simulate_icims_parsing(text)
    assert res["compatibility_score"] >= 85
    assert res["is_safe"] is True
    assert res["extracted_entities"]["contact"]["email"] == "jane.doe@example.com"
    assert "Work Experience" in res["extracted_entities"]["detected_sections"]
    assert "Education" in res["extracted_entities"]["detected_sections"]

def test_icims_simulator_missing_sections_and_tab_hazard():
    text = """
    John Smith
    Software Developer

    Projects
    Some cool project                     2021 - 2022
    Another project                       2020 - 2021
    Third project                         2019 - 2020
    Fourth project                        2018 - 2019
    """
    res = simulate_icims_parsing(text)
    assert res["compatibility_score"] < 70
    assert res["is_safe"] is False
    assert any("No primary email" in h for h in res["hazards"])
    assert any("columnar gaps" in h for h in res["hazards"])

def test_multi_ats_simulation_includes_icims():
    text = """
    Alice Wonderland
    alice@wonderland.io | (555) 987-6543 | linkedin.com/in/alicew

    Professional Summary
    Senior Backend Architect with 8+ years building enterprise distributed services.

    Work Experience
    Senior Backend Architect - Tech Corp
    Jan 2021 - Present
    - Developed distributed streaming pipelines using Kafka and Go.
    - Mentored 12 junior engineers and led sprint planning.
    - Optimized database query performance by 35%.

    Education
    M.S. in Software Engineering - Tech University
    2018 - 2020

    Skills
    Go, Kafka, Kubernetes, Distributed Systems, Python, AWS, Docker, PostgreSQL
    """
    multi_res = run_multi_ats_simulation(text)
    assert "icims" in multi_res["engines"]
    assert multi_res["engines"]["icims"]["compatibility_score"] >= 80
    assert multi_res["overall_cross_ats_score"] >= 80
