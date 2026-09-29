"""
Unit tests for benchmark runner and latency profiler.
"""

import time
from app.benchmark_runner import run_latency_benchmark

def dummy_fast_eval(r_text: str, jd_text: str):
    time.sleep(0.005)
    return {"status": "ok"}

def test_run_latency_benchmark_sla_pass():
    sample_text = "Experienced Senior Engineer with Python, Go, Docker, AWS " * 50
    jd_text = "Python Go Docker AWS"
    
    res = run_latency_benchmark(
        evaluation_func=dummy_fast_eval,
        resume_text=sample_text,
        jd_text=jd_text,
        iterations=5,
        sla_seconds=1.5
    )
    
    assert res["iterations"] == 5
    assert res["tokens_evaluated"] > 100
    assert res["avg_latency_ms"] > 0
    assert res["tokens_per_second"] > 0
    assert res["sla_passed"] is True

def test_run_latency_benchmark_sla_fail():
    def dummy_slow_eval(r, j):
        time.sleep(0.1)
        return {"status": "ok"}

    res = run_latency_benchmark(
        evaluation_func=dummy_slow_eval,
        resume_text="Hello world",
        jd_text="Job",
        iterations=3,
        sla_seconds=0.05
    )
    
    assert res["sla_passed"] is False
