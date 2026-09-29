"""
Module: domain_taxonomy.py
Purpose: Specialized ontological domain taxonomies and industry-calibrated scoring weights
for FinTech, Cloud/DevOps/SRE, and Machine Learning/AI Engineering roles.
"""

from typing import Dict, Any, List, Set

DOMAIN_TAXONOMIES: Dict[str, Dict[str, Any]] = {
    "FINTECH": {
        "core_skills": {
            "pci-dss", "fix protocol", "swift", "iso 20022", "low latency", "order routing",
            "market data", "distributed ledger", "smart contracts", "solidity", "algo trading",
            "risk engine", "idempotency", "settlement", "payment gateway", "fraud detection"
        },
        "target_hard_soft_ratio": 0.75,
        "keywords_weight": 0.45,
        "xyz_weight": 0.35,
    },
    "CLOUD_DEVOPS": {
        "core_skills": {
            "kubernetes", "docker", "terraform", "helm", "aws", "gcp", "azure", "ci/cd",
            "prometheus", "grafana", "istio", "argocd", "ansible", "linux", "gitops",
            "site reliability", "chaos engineering", "iac", "observability", "opentelemetry"
        },
        "target_hard_soft_ratio": 0.80,
        "keywords_weight": 0.40,
        "xyz_weight": 0.35,
    },
    "AI_ML": {
        "core_skills": {
            "pytorch", "tensorflow", "transformer", "huggingface", "fine-tuning", "rag",
            "langchain", "llamaindex", "cuda", "vector database", "embeddings", "onnx",
            "model quantization", "lora", "rlhf", "triton", "feature store", "mlflow", "wandb"
        },
        "target_hard_soft_ratio": 0.75,
        "keywords_weight": 0.40,
        "xyz_weight": 0.35,
    }
}


def classify_domain(text: str) -> Dict[str, Any]:
    """
    Classifies a resume or JD into the highest-matching specialized engineering domain.
    """
    text_lower = text.lower()
    scores = {}

    for domain, config in DOMAIN_TAXONOMIES.items():
        matched = {kw for kw in config["core_skills"] if kw in text_lower}
        scores[domain] = {
            "match_count": len(matched),
            "matched_skills": sorted(list(matched)),
            "coverage": len(matched) / len(config["core_skills"])
        }

    best_domain = max(scores.keys(), key=lambda d: scores[d]["match_count"])
    best_match = scores[best_domain]

    # If insufficient signal, return GENERAL
    if best_match["match_count"] < 2:
        return {
            "domain": "GENERAL_SOFTWARE",
            "confidence": 0.0,
            "matched_skills": [],
            "all_scores": scores
        }

    return {
        "domain": best_domain,
        "confidence": round(best_match["coverage"], 3),
        "matched_skills": best_match["matched_skills"],
        "recommended_weights": {
            "keywords": DOMAIN_TAXONOMIES[best_domain]["keywords_weight"],
            "xyz": DOMAIN_TAXONOMIES[best_domain]["xyz_weight"]
        },
        "all_scores": scores
    }
