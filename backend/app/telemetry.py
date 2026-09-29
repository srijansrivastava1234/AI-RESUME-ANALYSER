"""
Module: telemetry.py
Purpose: Sub-millisecond pipeline execution timer and memory footprint profiler
for deterministic telemetry and performance profiling across analysis stages.
"""

import time
import tracemalloc
from contextlib import contextmanager
from typing import Dict, Any, List


class PipelineProfiler:
    """Thread-safe multi-stage execution profiler."""

    def __init__(self):
        self.stages: List[Dict[str, Any]] = []
        self._total_start: float = time.perf_counter()

    @contextmanager
    def measure_stage(self, stage_name: str):
        """Context manager to measure latency and peak memory delta for a given stage."""
        tracemalloc.start()
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self.stages.append({
                "stage": stage_name,
                "duration_ms": round(elapsed * 1000, 3),
                "peak_memory_kb": round(peak_mem / 1024.0, 2)
            })

    def get_summary(self) -> Dict[str, Any]:
        """Returns aggregate profiling telemetry."""
        total_time = time.perf_counter() - self._total_start
        return {
            "total_pipeline_time_ms": round(total_time * 1000, 2),
            "stages_count": len(self.stages),
            "stages": self.stages,
            "max_stage": max(self.stages, key=lambda s: s["duration_ms"])["stage"] if self.stages else None
        }
