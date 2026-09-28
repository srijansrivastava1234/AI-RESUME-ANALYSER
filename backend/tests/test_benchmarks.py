import time
import pytest
from app.bm25_scorer import compute_bm25_plus as calculate_bm25_score
from app.layout_linearizer import simulate_recursive_xy_cut

def test_bm25_performance_benchmark():
    query_tokens = ["python", "fastapi", "react", "docker", "kubernetes", "aws", "postgresql"]
    corpus_document = (
        "Senior Software Engineer with extensive experience in Python, FastAPI microservices, "
        "and React frontend development. Architected cloud-native systems on AWS using Docker, "
        "Kubernetes, and managed PostgreSQL databases. Engineered high-throughput data pipelines."
    )
    
    start_time = time.perf_counter()
    for _ in range(100):
        _ = calculate_bm25_score(corpus_document, query_tokens)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    # 100 evaluations should complete comfortably under 100ms
    assert elapsed_ms < 100.0, f"BM25 benchmark took {elapsed_ms:.2f}ms (threshold: 100ms)"

def test_xycut_linearizer_performance_benchmark():
    sample_text = (
        "Skills: Python, Go        Acme Corp - Lead Engineer\n"
        "Tools: Docker, K8s        Architected multi-region cloud cluster\n"
        "Contact: jane@test.com    Decreased API latency by 45% using Redis\n"
        "Education: BS CS 2020     Mentored 8 junior and mid-level developers\n"
        "Languages: English        Managed $1.2M annual AWS cloud infrastructure\n"
    )
    
    start_time = time.perf_counter()
    for _ in range(100):
        _ = simulate_recursive_xy_cut(sample_text)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    # 100 layout evaluations should complete under 100ms
    assert elapsed_ms < 100.0, f"XYCut benchmark took {elapsed_ms:.2f}ms (threshold: 100ms)"
