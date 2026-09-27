import time
import pytest
from app.bm25 import calculate_bm25_score
from app.pdf_layout import XYCutLinearizer

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
    mock_bounding_boxes = [
        {"x0": 50, "y0": 100, "x1": 250, "y1": 120, "text": "Senior Software Engineer"},
        {"x0": 50, "y0": 130, "x1": 250, "y1": 150, "text": "Google Inc. (2020 - Present)"},
        {"x0": 300, "y0": 100, "x1": 500, "y1": 120, "text": "Skills: Python, FastAPI"},
        {"x0": 300, "y0": 130, "x1": 500, "y1": 150, "text": "Certifications: AWS Solution Architect"},
    ]
    
    linearizer = XYCutLinearizer(gutter_threshold_pt=12.0)
    
    start_time = time.perf_counter()
    for _ in range(50):
        _ = linearizer.linearize(mock_bounding_boxes)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    # 50 layout evaluations should complete under 100ms
    assert elapsed_ms < 100.0, f"XYCut benchmark took {elapsed_ms:.2f}ms (threshold: 100ms)"
