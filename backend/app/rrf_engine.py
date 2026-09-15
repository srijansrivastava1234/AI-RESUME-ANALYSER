"""
Reciprocal Rank Fusion (RRF) Multi-Metric Candidate Scoring Engine.

Grounded in Information Retrieval (IR) standards (Cormack, Clarke, & Buettcher 2009)
and the ATS Validator Architecture:
- Combines disparate ranking dimensions (Lexical Keyword Recall, Google/IBM XYZ Impact,
  Structural Parseability, Readability Grade) into a mathematically robust composite rank.
- Formula: RRF_score(d) = SUM_{m in M} [ 1 / (k + r_m(d)) ]
- Default smoothing constant: k = 60
- Eliminates score scale distortion and normalizes candidate ranking across multi-system evaluations.
"""

from typing import Dict, List, Any, Optional


def compute_rrf_from_rank_lists(
    rankings: Dict[str, List[str]],
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Computes Reciprocal Rank Fusion (RRF) scores across multiple system rankings.

    :param rankings: Dictionary mapping system/metric name to an ordered list of candidate IDs (best first).
    :param k: Canonical RRF smoothing constant (default 60).
    :return: List of sorted candidate dictionaries with rrf_score, normalized_score, rank, and system breakdowns.
    """
    if not rankings:
        return []

    # Map candidate_id -> total_rrf_score and metric ranks
    candidate_scores: Dict[str, float] = {}
    candidate_metric_ranks: Dict[str, Dict[str, int]] = {}

    for system_name, candidate_list in rankings.items():
        for rank_idx, candidate_id in enumerate(candidate_list):
            rank = rank_idx + 1  # 1-indexed rank
            reciprocal_value = 1.0 / (k + rank)

            if candidate_id not in candidate_scores:
                candidate_scores[candidate_id] = 0.0
                candidate_metric_ranks[candidate_id] = {}

            candidate_scores[candidate_id] += reciprocal_value
            candidate_metric_ranks[candidate_id][system_name] = rank

    if not candidate_scores:
        return []

    # Calculate max possible score if a candidate was ranked #1 across all provided systems
    num_systems = len(rankings)
    max_theoretical_score = num_systems * (1.0 / (k + 1)) if num_systems > 0 else 1.0

    # Sort candidates by descending RRF score, breaking ties by lowest average rank
    def sort_key(item):
        cand_id, score = item
        ranks = candidate_metric_ranks[cand_id].values()
        avg_rank = sum(ranks) / len(ranks) if ranks else 999.0
        return (-score, avg_rank, cand_id)

    sorted_candidates = sorted(candidate_scores.items(), key=sort_key)

    results: List[Dict[str, Any]] = []
    for rank_idx, (cand_id, score) in enumerate(sorted_candidates):
        normalized_score = round((score / max_theoretical_score) * 100, 2)
        results.append({
            "candidate_id": cand_id,
            "rank": rank_idx + 1,
            "rrf_score": round(score, 6),
            "normalized_score": min(100.0, max(0.0, normalized_score)),
            "metric_ranks": candidate_metric_ranks[cand_id]
        })

    return results


def fuse_candidate_evaluations(
    candidates: List[Dict[str, Any]],
    metric_keys: Optional[List[str]] = None,
    id_key: str = "id",
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Fuses multiple quantitative scores of candidates into a unified RRF ranking.

    :param candidates: List of candidate dictionaries containing numeric metrics.
    :param metric_keys: List of numerical metric keys to rank on (e.g. ['keyword_score', 'xyz_score']).
                        If None, auto-detects numerical keys present across candidates.
    :param id_key: Key identifying the candidate unique ID or name.
    :param k: Canonical RRF smoothing constant (default 60).
    :return: List of candidates enriched with 'rrf_rank', 'rrf_score', 'rrf_normalized_score'.
    """
    if not candidates:
        return []

    if len(candidates) == 1:
        single = dict(candidates[0])
        single["rrf_rank"] = 1
        single["rrf_score"] = round(1.0 / (k + 1), 6)
        single["rrf_normalized_score"] = 100.0
        single["metric_ranks"] = {}
        return [single]

    # Auto-detect numeric metric keys if not supplied
    if not metric_keys:
        sample = candidates[0]
        metric_keys = [
            key for key, val in sample.items()
            if key != id_key and isinstance(val, (int, float)) and not isinstance(val, bool)
        ]

    if not metric_keys:
        # Fallback: maintain original order
        return [
            {**cand, "rrf_rank": i + 1, "rrf_score": 0.0, "rrf_normalized_score": 0.0, "metric_ranks": {}}
            for i, cand in enumerate(candidates)
        ]

    # Build rank lists for each metric
    rankings: Dict[str, List[str]] = {}
    candidate_map: Dict[str, Dict[str, Any]] = {}

    for cand in candidates:
        cand_id = str(cand.get(id_key, id(cand)))
        candidate_map[cand_id] = cand

    for metric in metric_keys:
        # Sort candidates descending by this metric value
        sorted_for_metric = sorted(
            candidates,
            key=lambda c: float(c.get(metric, 0.0)),
            reverse=True
        )
        rankings[metric] = [str(c.get(id_key, id(c))) for c in sorted_for_metric]

    rrf_results = compute_rrf_from_rank_lists(rankings, k=k)

    # Merge results back into candidate dicts
    final_output: List[Dict[str, Any]] = []
    for rrf_item in rrf_results:
        cand_id = rrf_item["candidate_id"]
        original = dict(candidate_map[cand_id])
        original["rrf_rank"] = rrf_item["rank"]
        original["rrf_score"] = rrf_item["rrf_score"]
        original["rrf_normalized_score"] = rrf_item["normalized_score"]
        original["metric_ranks"] = rrf_item["metric_ranks"]
        final_output.append(original)

    return final_output
