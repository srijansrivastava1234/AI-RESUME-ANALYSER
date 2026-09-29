"""
Unit tests for domain taxonomy classifier.
"""

from app.domain_taxonomy import classify_domain

def test_classify_domain_devops():
    text = "Senior SRE with deep experience in Kubernetes, Terraform, Docker, AWS, Prometheus, and Helm."
    res = classify_domain(text)
    assert res["domain"] == "CLOUD_DEVOPS"
    assert "kubernetes" in res["matched_skills"]
    assert "terraform" in res["matched_skills"]
    assert res["confidence"] > 0.2

def test_classify_domain_ai_ml():
    text = "Machine Learning Engineer specializing in PyTorch, Transformer architectures, Fine-Tuning, LoRA, and RAG pipelines."
    res = classify_domain(text)
    assert res["domain"] == "AI_ML"
    assert "pytorch" in res["matched_skills"]
    assert "rag" in res["matched_skills"]

def test_classify_domain_fintech():
    text = "Quant Developer building low latency order routing, FIX protocol parsers, and risk engine microservices."
    res = classify_domain(text)
    assert res["domain"] == "FINTECH"
    assert "fix protocol" in res["matched_skills"]

def test_classify_domain_general():
    text = "I worked on a website and fixed some styling bugs."
    res = classify_domain(text)
    assert res["domain"] == "GENERAL_SOFTWARE"
