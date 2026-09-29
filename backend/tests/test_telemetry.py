"""
Unit tests for pipeline telemetry profiler.
"""

import time
from app.telemetry import PipelineProfiler

def test_pipeline_profiler_stages():
    profiler = PipelineProfiler()
    
    with profiler.measure_stage("text_extraction"):
        data = [i for i in range(1000)]
        time.sleep(0.005)
        
    with profiler.measure_stage("bm25_scoring"):
        data = [i * 2 for i in range(5000)]
        time.sleep(0.008)
        
    summary = profiler.get_summary()
    assert summary["stages_count"] == 2
    assert summary["total_pipeline_time_ms"] > 0
    assert summary["stages"][0]["stage"] == "text_extraction"
    assert summary["stages"][0]["duration_ms"] > 0
    assert summary["stages"][0]["peak_memory_kb"] >= 0
    assert summary["max_stage"] in ["text_extraction", "bm25_scoring"]
