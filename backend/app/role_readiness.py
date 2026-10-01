"""
Target Role Readiness Index & Archetype Gap Matrix Engine.
Audits candidate qualification density against standardized technical archetypes
(Backend, Frontend, Fullstack, ML/AI, DevOps/Platform, Data Engineering)
using category-weighted multi-dimensional competency models.
"""

import re
from typing import Dict, Any, List, Optional

ROLE_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "backend_engineer": {
        "title": "Backend Software Engineer",
        "categories": {
            "languages": {
                "weight": 25.0,
                "skills": ["python", "go", "golang", "java", "c#", "c++", "rust", "node.js", "ruby"],
                "min_target": 1
            },
            "frameworks": {
                "weight": 20.0,
                "skills": ["fastapi", "django", "flask", "spring", "express", "nest.js", "gin"],
                "min_target": 1
            },
            "databases": {
                "weight": 20.0,
                "skills": ["sql", "postgresql", "mysql", "mongodb", "redis", "dynamodb"],
                "min_target": 1
            },
            "infrastructure": {
                "weight": 20.0,
                "skills": ["docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "kafka", "rabbitmq"],
                "min_target": 1
            },
            "architecture": {
                "weight": 15.0,
                "skills": ["rest", "microservices", "grpc", "graphql", "distributed systems", "api"],
                "min_target": 1
            }
        }
    },
    "frontend_engineer": {
        "title": "Frontend Software Engineer",
        "categories": {
            "languages": {
                "weight": 30.0,
                "skills": ["javascript", "typescript", "html", "css"],
                "min_target": 2
            },
            "frameworks": {
                "weight": 30.0,
                "skills": ["react", "next.js", "vue", "angular", "svelte"],
                "min_target": 1
            },
            "styling_tooling": {
                "weight": 20.0,
                "skills": ["tailwind", "sass", "css modules", "vite", "webpack", "redux", "zustand"],
                "min_target": 1
            },
            "testing_quality": {
                "weight": 20.0,
                "skills": ["jest", "cypress", "playwright", "accessibility", "responsive design"],
                "min_target": 1
            }
        }
    },
    "fullstack_engineer": {
        "title": "Full-Stack Engineer",
        "categories": {
            "frontend": {
                "weight": 30.0,
                "skills": ["react", "next.js", "vue", "javascript", "typescript", "html", "css"],
                "min_target": 2
            },
            "backend": {
                "weight": 30.0,
                "skills": ["node.js", "python", "fastapi", "django", "express", "go", "java"],
                "min_target": 1
            },
            "databases": {
                "weight": 20.0,
                "skills": ["sql", "postgresql", "mongodb", "mysql", "redis"],
                "min_target": 1
            },
            "devops_cloud": {
                "weight": 20.0,
                "skills": ["docker", "aws", "gcp", "git", "ci/cd", "rest"],
                "min_target": 1
            }
        }
    },
    "ml_engineer": {
        "title": "Machine Learning Engineer",
        "categories": {
            "core_ml": {
                "weight": 35.0,
                "skills": ["python", "pytorch", "tensorflow", "scikit-learn", "machine learning", "deep learning"],
                "min_target": 2
            },
            "data_processing": {
                "weight": 25.0,
                "skills": ["pandas", "numpy", "sql", "spark", "pyspark"],
                "min_target": 2
            },
            "llm_genai": {
                "weight": 20.0,
                "skills": ["transformers", "huggingface", "llm", "langchain", "llamaindex", "rag"],
                "min_target": 1
            },
            "mlops_deploy": {
                "weight": 20.0,
                "skills": ["mlops", "docker", "fastapi", "aws", "gcp", "kubeflow", "mlflow"],
                "min_target": 1
            }
        }
    },
    "devops_platform_engineer": {
        "title": "DevOps / Platform Engineer",
        "categories": {
            "containers_k8s": {
                "weight": 30.0,
                "skills": ["kubernetes", "docker", "helm", "k8s"],
                "min_target": 1
            },
            "iac_automation": {
                "weight": 25.0,
                "skills": ["terraform", "ansible", "cloudformation", "pulumi"],
                "min_target": 1
            },
            "ci_cd_gitops": {
                "weight": 25.0,
                "skills": ["ci/cd", "github actions", "gitlab ci", "jenkins", "argocd", "gitops"],
                "min_target": 1
            },
            "cloud_os": {
                "weight": 20.0,
                "skills": ["aws", "gcp", "azure", "linux", "bash", "prometheus", "grafana"],
                "min_target": 2
            }
        }
    },
    "data_engineer": {
        "title": "Data Platform Engineer",
        "categories": {
            "languages_query": {
                "weight": 30.0,
                "skills": ["python", "sql", "scala", "pyspark"],
                "min_target": 2
            },
            "big_data_processing": {
                "weight": 25.0,
                "skills": ["spark", "kafka", "flink", "databricks", "hadoop", "etl"],
                "min_target": 2
            },
            "warehousing": {
                "weight": 25.0,
                "skills": ["bigquery", "snowflake", "redshift", "dbt", "data warehouse"],
                "min_target": 1
            },
            "orchestration": {
                "weight": 20.0,
                "skills": ["airflow", "prefect", "dagster", "docker", "aws", "gcp"],
                "min_target": 1
            }
        }
    }
}

def evaluate_role_readiness(
    resume_text: str,
    target_role: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates candidate resume text against target role archetypes using
    category-based coverage and upskilling gap matrices.
    """
    if not resume_text or not resume_text.strip():
        return {
            "target_role": target_role or "backend_engineer",
            "role_title": ROLE_ARCHETYPES.get(target_role or "backend_engineer", {}).get("title", "Software Engineer"),
            "readiness_score": 0.0,
            "readiness_tier": "Pivot Required",
            "matched_skills": [],
            "missing_critical_skills": [],
            "category_breakdown": {},
            "all_role_scores": {},
            "recommendations": ["Provide resume text to calculate archetype readiness."]
        }

    lower_text = resume_text.lower()

    def score_single_archetype(role_key: str) -> Dict[str, Any]:
        archetype = ROLE_ARCHETYPES[role_key]
        total_score = 0.0
        all_matched = []
        missing_critical = []
        category_breakdown = {}

        for cat_name, cat_data in archetype["categories"].items():
            cat_weight = cat_data["weight"]
            cat_skills = cat_data["skills"]
            min_target = cat_data["min_target"]

            cat_matches = [
                s for s in cat_skills
                if re.search(r"\b" + re.escape(s) + r"\b", lower_text)
            ]
            all_matched.extend(cat_matches)

            # Ratio of min target achieved
            coverage_ratio = min(1.0, len(cat_matches) / min_target) if min_target > 0 else 1.0
            cat_score = round(coverage_ratio * cat_weight, 1)
            total_score += cat_score

            if len(cat_matches) < min_target:
                missing_in_cat = [s for s in cat_skills if s not in cat_matches][:2]
                missing_critical.extend(missing_in_cat)

            category_breakdown[cat_name] = {
                "score": cat_score,
                "max_score": cat_weight,
                "matched": cat_matches,
                "coverage_pct": round(coverage_ratio * 100, 1)
            }

        final_score = round(min(100.0, total_score), 1)

        if final_score >= 80:
            tier = "Ready"
        elif final_score >= 60:
            tier = "Strong Candidate"
        elif final_score >= 40:
            tier = "Upskilling Needed"
        else:
            tier = "Pivot Required"

        return {
            "readiness_score": final_score,
            "readiness_tier": tier,
            "matched_skills": list(set(all_matched)),
            "missing_critical_skills": list(set(missing_critical)),
            "category_breakdown": category_breakdown
        }

    # Score all archetypes
    all_results = {k: score_single_archetype(k) for k in ROLE_ARCHETYPES}
    all_scores = {k: all_results[k]["readiness_score"] for k in ROLE_ARCHETYPES}

    # Select primary target
    effective_role = target_role if (target_role and target_role in ROLE_ARCHETYPES) else max(all_scores, key=all_scores.get)
    target_eval = all_results[effective_role]
    role_title = ROLE_ARCHETYPES[effective_role]["title"]

    recommendations = []
    if target_eval["missing_critical_skills"]:
        top_missing = ", ".join(s.upper() if len(s) <= 4 else s.title() for s in target_eval["missing_critical_skills"][:3])
        recommendations.append(f"Strengthen category coverage for {role_title}: Add experience with {top_missing}.")
    if target_eval["readiness_score"] >= 80:
        recommendations.append(f"Exceptional qualification alignment ({target_eval['readiness_score']}%) with {role_title} industry baseline.")
    elif target_eval["readiness_score"] >= 60:
        recommendations.append(f"Solid foundation ({target_eval['readiness_score']}%) for {role_title}; closing 1-2 tooling gaps will elevate to top candidate tier.")

    return {
        "target_role": effective_role,
        "role_title": role_title,
        "readiness_score": target_eval["readiness_score"],
        "readiness_tier": target_eval["readiness_tier"],
        "matched_skills": target_eval["matched_skills"],
        "missing_critical_skills": target_eval["missing_critical_skills"],
        "category_breakdown": target_eval["category_breakdown"],
        "all_role_scores": all_scores,
        "recommendations": recommendations
    }
