import pytest
from app.rrf_engine import compute_rrf_from_rank_lists, fuse_candidate_evaluations


def test_compute_rrf_standard_rankings():
    # 3 candidates evaluated across 2 ranking systems (Keyword Match & XYZ Score)
    rankings = {
        "keyword": ["cand_A", "cand_B", "cand_C"],
        "xyz": ["cand_B", "cand_A", "cand_C"]
    }
    results = compute_rrf_from_rank_lists(rankings, k=60)
    assert len(results) == 3

    # cand_A: 1/(60+1) + 1/(60+2) = 1/61 + 1/62
    # cand_B: 1/(60+2) + 1/(60+1) = 1/62 + 1/61
    # Scores for A and B should be identical
    assert results[0]["rrf_score"] == results[1]["rrf_score"]
    # cand_C: 1/(60+3) + 1/(60+3) = 2/63, should be lowest
    assert results[2]["candidate_id"] == "cand_C"
    assert results[2]["rank"] == 3
    assert results[2]["rrf_score"] < results[0]["rrf_score"]


def test_compute_rrf_empty():
    assert compute_rrf_from_rank_lists({}) == []
    assert compute_rrf_from_rank_lists({"empty_sys": []}) == []


def test_compute_rrf_normalized_score():
    # If candidate is #1 in all systems, normalized score should be 100
    rankings = {
        "sys1": ["star_candidate"],
        "sys2": ["star_candidate"],
        "sys3": ["star_candidate"]
    }
    results = compute_rrf_from_rank_lists(rankings, k=60)
    assert len(results) == 1
    assert results[0]["normalized_score"] == 100.0
    assert results[0]["rank"] == 1


def test_fuse_candidate_evaluations_multimetric():
    candidates = [
        {"id": "cand_1", "name": "Alice", "keyword_score": 95, "xyz_score": 70, "hygiene": 80},
        {"id": "cand_2", "name": "Bob", "keyword_score": 60, "xyz_score": 98, "hygiene": 95},
        {"id": "cand_3", "name": "Charlie", "keyword_score": 50, "xyz_score": 50, "hygiene": 60},
    ]
    fused = fuse_candidate_evaluations(candidates, metric_keys=["keyword_score", "xyz_score", "hygiene"])
    assert len(fused) == 3
    # Top two should be Alice and Bob
    top_ids = {fused[0]["id"], fused[1]["id"]}
    assert top_ids == {"cand_1", "cand_2"}
    assert fused[2]["id"] == "cand_3"
    assert fused[2]["rrf_rank"] == 3
    assert fused[0]["rrf_score"] > fused[2]["rrf_score"]


def test_fuse_candidate_evaluations_edge_cases():
    # Empty
    assert fuse_candidate_evaluations([]) == []

    # Single candidate
    single = fuse_candidate_evaluations([{"id": "c1", "score": 80}])
    assert len(single) == 1
    assert single[0]["rrf_rank"] == 1
    assert single[0]["rrf_normalized_score"] == 100.0

    # Auto-detection of metric keys
    cands = [
        {"id": "a", "metric_a": 10, "metric_b": 20},
        {"id": "b", "metric_a": 20, "metric_b": 10}
    ]
    fused_auto = fuse_candidate_evaluations(cands)
    assert len(fused_auto) == 2
    assert "rrf_rank" in fused_auto[0]
