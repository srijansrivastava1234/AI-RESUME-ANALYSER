"""
Module: benchmark_runner.py
Purpose: Automated performance profiler, latency SLA evaluator (<1.5s),
and token throughput benchmark engine for end-to-end resume evaluation pipelines.
"""

import time
from typing import Dict, Any, Callable


def run_latency_benchmark(
    evaluation_func: Callable[[str, str], Dict[str, Any]],
    resume_text: str,
    jd_text: str,
    iterations: int = 5,
    sla_seconds: float = 1.5
) -> Dict[str, Any]:
    """
    Executes multiple benchmark runs to compute latency percentiles (P50, P95, P99),
    token throughput per second, and SLA compliance.
    """
    latencies = []
    token_count = len(resume_text.split())

    for _ in range(iterations):
        t0 = time.perf_counter()
        evaluation_func(resume_text, jd_text)
        t1 = time.perf_counter()
        latencies.append(t1 - t0)

    latencies.sort()
    avg_latency = sum(latencies) / len(latencies)
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[-1]
    
    tokens_per_sec = (token_count / avg_latency) if avg_latency > 0 else 0.0

    return {
        "iterations": iterations,
        "tokens_evaluated": token_count,
        "avg_latency_ms": round(avg_latency * 1000, 2),
        "p50_latency_ms": round(p50 * 1000, 2),
        "p95_latency_ms": round(p95 * 1000, 2),
        "p99_latency_ms": round(p99 * 1000, 2),
        "tokens_per_second": round(tokens_per_sec, 2),
        "sla_target_seconds": sla_seconds,
        "sla_passed": p95 <= sla_seconds
    }
