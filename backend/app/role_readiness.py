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
    },
    "registered_nurse": {
        "title": "Registered Nurse / Healthcare Specialist",
        "categories": {
            "clinical_practice": {
                "weight": 35.0,
                "skills": ["patient care", "triage", "iv therapy", "iv administration", "vital signs", "wound care", "phlebotomy", "catheterization"],
                "min_target": 2
            },
            "charting_systems": {
                "weight": 25.0,
                "skills": ["epic", "cerner", "ehr", "emr", "meditech"],
                "min_target": 1
            },
            "compliance_protocols": {
                "weight": 20.0,
                "skills": ["bls", "acls", "hipaa", "infection control", "osha", "cpr"],
                "min_target": 1
            },
            "specialty_care": {
                "weight": 20.0,
                "skills": ["icu", "er", "telemetry", "pediatrics", "medication administration"],
                "min_target": 1
            }
        }
    },
    "accountant_auditor": {
        "title": "Accountant / Financial Auditor",
        "categories": {
            "accounting_standards": {
                "weight": 35.0,
                "skills": ["gaap", "ifrs", "general ledger", "reconciliation", "journal entries", "financial reporting"],
                "min_target": 2
            },
            "financial_software": {
                "weight": 25.0,
                "skills": ["excel", "quickbooks", "sap", "netsuite", "xero", "erp"],
                "min_target": 1
            },
            "compliance_tax": {
                "weight": 20.0,
                "skills": ["tax preparation", "internal audit", "sox", "taxation", "variance analysis"],
                "min_target": 1
            },
            "credentials_analysis": {
                "weight": 20.0,
                "skills": ["cpa", "cma", "accounts payable", "accounts receivable", "financial modeling"],
                "min_target": 1
            }
        }
    },
    "digital_marketer": {
        "title": "Digital Marketing Specialist",
        "categories": {
            "growth_acquisition": {
                "weight": 35.0,
                "skills": ["seo", "sem", "meta ads", "google ads", "content marketing", "email marketing"],
                "min_target": 2
            },
            "analytics_metrics": {
                "weight": 25.0,
                "skills": ["google analytics", "ga4", "looker", "conversion rate", "roas", "cac"],
                "min_target": 1
            },
            "tooling_crm": {
                "weight": 20.0,
                "skills": ["hubspot", "salesforce", "mailchimp", "semrush", "ahrefs"],
                "min_target": 1
            },
            "strategy": {
                "weight": 20.0,
                "skills": ["pipeline management", "lead generation", "a/b testing", "funnel optimization"],
                "min_target": 1
            }
        }
    },
    "sales_executive": {
        "title": "Account Executive / B2B Sales",
        "categories": {
            "pipeline_closing": {
                "weight": 35.0,
                "skills": ["b2b sales", "prospecting", "lead generation", "cold outreach", "negotiation", "quota"],
                "min_target": 2
            },
            "sales_stack": {
                "weight": 25.0,
                "skills": ["salesforce", "hubspot", "crm", "outreach", "linkedin sales navigator"],
                "min_target": 1
            },
            "relationship_management": {
                "weight": 20.0,
                "skills": ["account management", "contract negotiation", "client retention", "customer success"],
                "min_target": 1
            },
            "forecasting": {
                "weight": 20.0,
                "skills": ["sales forecasting", "pipeline management", "deal closing", "revenue growth"],
                "min_target": 1
            }
        }
    },
    "hr_specialist": {
        "title": "Human Resources Specialist / People Ops",
        "categories": {
            "talent_acquisition": {
                "weight": 35.0,
                "skills": ["recruiting", "talent acquisition", "sourcing", "onboarding", "interviewing"],
                "min_target": 2
            },
            "people_systems": {
                "weight": 25.0,
                "skills": ["workday", "adp", "hris", "bamboohr", "greenhouse"],
                "min_target": 1
            },
            "employee_relations": {
                "weight": 20.0,
                "skills": ["employee relations", "performance management", "retention", "benefits administration"],
                "min_target": 1
            },
            "compliance_labor": {
                "weight": 20.0,
                "skills": ["labor laws", "compliance", "eeoc", "workplace safety", "flsa"],
                "min_target": 1
            }
        }
    },
    "operations_manager": {
        "title": "Operations & Supply Chain Manager",
        "categories": {
            "supply_chain_logistics": {
                "weight": 35.0,
                "skills": ["supply chain", "logistics", "procurement", "inventory management", "vendor management"],
                "min_target": 2
            },
            "operational_excellence": {
                "weight": 25.0,
                "skills": ["six sigma", "lean", "process optimization", "quality assurance", "kaizen"],
                "min_target": 1
            },
            "enterprise_systems": {
                "weight": 20.0,
                "skills": ["erp", "sap", "oracle", "wms"],
                "min_target": 1
            },
            "business_impact": {
                "weight": 20.0,
                "skills": ["budget management", "cost reduction", "kpi tracking", "resource allocation"],
                "min_target": 1
            }
        }
    },
    "legal_counsel": {
        "title": "Legal Counsel / Attorney",
        "categories": {
            "contract_drafting": {
                "weight": 35.0,
                "skills": ["contract drafting", "contract negotiation", "m&a", "due diligence"],
                "min_target": 2
            },
            "litigation_research": {
                "weight": 25.0,
                "skills": ["litigation", "legal research", "statutory interpretation", "brief writing"],
                "min_target": 1
            },
            "corporate_governance": {
                "weight": 20.0,
                "skills": ["corporate governance", "compliance", "regulatory filings", "risk management"],
                "min_target": 1
            },
            "specialized_law": {
                "weight": 20.0,
                "skills": ["intellectual property", "employment law", "privacy", "gdpr"],
                "min_target": 1
            }
        }
    },
    "product_designer": {
        "title": "Product & UX/UI Designer",
        "categories": {
            "design_tooling": {
                "weight": 35.0,
                "skills": ["figma", "sketch", "adobe xd", "photoshop", "illustrator"],
                "min_target": 2
            },
            "user_experience": {
                "weight": 25.0,
                "skills": ["wireframing", "prototyping", "design systems", "ui design", "ux design"],
                "min_target": 2
            },
            "research_testing": {
                "weight": 20.0,
                "skills": ["user research", "usability testing", "user journey", "persona development"],
                "min_target": 1
            },
            "collaboration": {
                "weight": 20.0,
                "skills": ["agile", "cross-functional", "developer handoff", "accessibility"],
                "min_target": 1
            }
        }
    },
    "project_manager": {
        "title": "Project & Program Manager",
        "categories": {
            "methodologies": {
                "weight": 35.0,
                "skills": ["agile", "scrum", "waterfall", "kanban", "sprint planning"],
                "min_target": 2
            },
            "tools_tracking": {
                "weight": 25.0,
                "skills": ["jira", "confluence", "trello", "asana", "ms project"],
                "min_target": 1
            },
            "delivery_governance": {
                "weight": 20.0,
                "skills": ["risk management", "scope management", "stakeholder management", "budget management"],
                "min_target": 1
            },
            "certifications": {
                "weight": 20.0,
                "skills": ["pmp", "csm", "prince2", "six sigma"],
                "min_target": 1
            }
        }
    },
    "general_professional": {
        "title": "Universal Corporate Professional",
        "categories": {
            "core_competencies": {
                "weight": 35.0,
                "skills": ["project management", "process improvement", "reporting", "operations", "analysis"],
                "min_target": 2
            },
            "business_tools": {
                "weight": 25.0,
                "skills": ["excel", "powerpoint", "word", "crm", "erp", "collaboration"],
                "min_target": 1
            },
            "cross_functional": {
                "weight": 20.0,
                "skills": ["stakeholder management", "client relations", "vendor management", "coordination"],
                "min_target": 1
            },
            "execution_governance": {
                "weight": 20.0,
                "skills": ["budgeting", "compliance", "scheduling", "quality assurance"],
                "min_target": 1
            }
        }
    }
}

# Fuzzy role matcher mapping aliases and job title keywords to archetype keys
ROLE_TITLE_PATTERNS = [
    (re.compile(r'\b(?:nurse|nursing|rn|clinical|hospital|patient care|icu|triage)\b', re.IGNORECASE), "registered_nurse"),
    (re.compile(r'\b(?:accountant|accounting|cpa|audit|auditor|tax|bookkeeper|general ledger)\b', re.IGNORECASE), "accountant_auditor"),
    (re.compile(r'\b(?:marketer|marketing|seo|sem|growth|social media|content strategist)\b', re.IGNORECASE), "digital_marketer"),
    (re.compile(r'\b(?:sales|account executive|bdr|sdr|business development|closing)\b', re.IGNORECASE), "sales_executive"),
    (re.compile(r'\b(?:human resources|hr|recruiter|recruiting|talent acquisition|people ops)\b', re.IGNORECASE), "hr_specialist"),
    (re.compile(r'\b(?:operations|supply chain|logistics|procurement|inventory)\b', re.IGNORECASE), "operations_manager"),
    (re.compile(r'\b(?:legal|lawyer|attorney|counsel|paralegal|litigation)\b', re.IGNORECASE), "legal_counsel"),
    (re.compile(r'\b(?:designer|ui|ux|product design|wireframe|figma)\b', re.IGNORECASE), "product_designer"),
    (re.compile(r'\b(?:project manager|program manager|scrum master|pmp|agile coach)\b', re.IGNORECASE), "project_manager"),
    (re.compile(r'\b(?:backend|python|go|golang|java|api|microservice|database)\b', re.IGNORECASE), "backend_engineer"),
    (re.compile(r'\b(?:frontend|react|vue|angular|web developer|ui developer)\b', re.IGNORECASE), "frontend_engineer"),
    (re.compile(r'\b(?:fullstack|full-stack|full stack|software engineer|software developer|sde)\b', re.IGNORECASE), "fullstack_engineer"),
    (re.compile(r'\b(?:machine learning|ml|ai|deep learning|data scientist|nlp|computer vision)\b', re.IGNORECASE), "ml_engineer"),
    (re.compile(r'\b(?:devops|sre|platform|cloud engineer|infrastructure|kubernetes|terraform)\b', re.IGNORECASE), "devops_platform_engineer"),
    (re.compile(r'\b(?:data engineer|etl|big data|spark|pipeline engineer|data platform)\b', re.IGNORECASE), "data_engineer"),
]

def resolve_role_archetype(raw_title: Optional[str]) -> Optional[str]:
    """
    Resolves an arbitrary job title string to the closest built-in archetype key.
    """
    if not raw_title:
        return None
    raw_clean = raw_title.strip().lower()
    
    # Direct key match
    if raw_clean in ROLE_ARCHETYPES:
        return raw_clean
    
    # Key with underscores
    slug = raw_clean.replace(" ", "_").replace("-", "_")
    if slug in ROLE_ARCHETYPES:
        return slug
        
    # Check regex patterns
    for pattern, archetype_key in ROLE_TITLE_PATTERNS:
        if pattern.search(raw_clean):
            return archetype_key
            
    return None

def generate_dynamic_role_archetype(role_name: str, context_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Synthesizes a 4-category competency archetype on the fly for any custom job title
    (e.g., Sommelier, Pilot, Construction Superintendent, Biotech Researcher).
    Uses Gemini when available, or provides a robust heuristic schema.
    """
    clean_title = role_name.strip().title()
    import os
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            import json
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            Create a standard 4-category ATS qualification archetype for the job role: "{clean_title}".
            Context (if any): {context_text[:500] if context_text else 'None'}
            Return strictly JSON with this schema:
            {{
              "title": "{clean_title}",
              "categories": {{
                "core_skills": {{"weight": 35.0, "skills": ["skill1", "skill2", "skill3"], "min_target": 2}},
                "tools_technologies": {{"weight": 25.0, "skills": ["tool1", "tool2"], "min_target": 1}},
                "governance_standards": {{"weight": 20.0, "skills": ["std1", "std2"], "min_target": 1}},
                "business_impact": {{"weight": 20.0, "skills": ["imp1", "imp2"], "min_target": 1}}
              }}
            }}
            """
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            parsed = json.loads(response.text.strip())
            if "categories" in parsed:
                return parsed
        except Exception:
            pass

    # Heuristic fallback archetype customized to title
    from app.keywords import extract_dynamic_job_keywords
    extracted = extract_dynamic_job_keywords(context_text or role_name, top_n=8)
    core = extracted[:4] if extracted else ["specialized domain expertise", "core execution", "process execution"]
    tools = extracted[4:8] if len(extracted) > 4 else ["industry software", "operational tooling"]

    return {
        "title": clean_title,
        "categories": {
            "core_qualifications": {
                "weight": 35.0,
                "skills": [s.lower() for s in core],
                "min_target": 2
            },
            "domain_tools": {
                "weight": 25.0,
                "skills": [s.lower() for s in tools],
                "min_target": 1
            },
            "standards_compliance": {
                "weight": 20.0,
                "skills": ["compliance", "quality assurance", "safety", "standards"],
                "min_target": 1
            },
            "operational_delivery": {
                "weight": 20.0,
                "skills": ["project management", "reporting", "stakeholder coordination", "delivery"],
                "min_target": 1
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
        resolved = resolve_role_archetype(target_role)
        role_key = resolved if (resolved and resolved in ROLE_ARCHETYPES) else (target_role or "backend_engineer")
        title = ROLE_ARCHETYPES.get(role_key, {}).get("title", target_role or "Software Engineer")
        return {
            "target_role": target_role or "backend_engineer",
            "role_title": title,
            "readiness_score": 0.0,
            "readiness_tier": "Pivot Required",
            "matched_skills": [],
            "missing_critical_skills": [],
            "category_breakdown": {},
            "all_role_scores": {},
            "recommendations": ["Provide resume text to calculate archetype readiness."]
        }

    lower_text = resume_text.lower()

    # Resolve or synthesize archetype for arbitrary job titles
    resolved_key = resolve_role_archetype(target_role)
    dynamic_archetype = None
    if target_role and not resolved_key and target_role not in ROLE_ARCHETYPES:
        dynamic_archetype = generate_dynamic_role_archetype(target_role, resume_text)
        resolved_key = "custom_dynamic_role"

    active_archetypes = dict(ROLE_ARCHETYPES)
    if dynamic_archetype:
        active_archetypes["custom_dynamic_role"] = dynamic_archetype

    def score_single_archetype(role_key: str) -> Dict[str, Any]:
        archetype = active_archetypes[role_key]
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

    # Score active archetypes
    all_results = {k: score_single_archetype(k) for k in active_archetypes}
    all_scores = {k: all_results[k]["readiness_score"] for k in active_archetypes}

    # Select primary target
    if target_role:
        if resolved_key and resolved_key in active_archetypes:
            effective_role = resolved_key
        elif target_role in active_archetypes:
            effective_role = target_role
        else:
            effective_role = max(all_scores, key=all_scores.get)
    else:
        effective_role = max(all_scores, key=all_scores.get)

    target_eval = all_results[effective_role]
    role_title = active_archetypes[effective_role]["title"]

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
