import re
from typing import Dict, Any, List, Optional

# High-impact action verbs (Weight w_X = 0.25)
POWER_ACTION_VERBS = {
    "architected", "engineered", "spearheaded", "optimized", "orchestrated",
    "implemented", "deployed", "automated", "streamlined", "formulated",
    "pioneered", "modernized", "accelerated", "designed", "constructed",
    "configured", "audited", "eliminated", "decoupled", "mitigated",
    "developed", "scaled", "centralized", "refactored", "integrated"
}

MEDIUM_ACTION_VERBS = {
    "built", "created", "led", "managed", "maintained", "updated",
    "delivered", "executed", "trained", "authored", "improved", "launched",
    "established", "reduced", "increased", "resolved"
}

# Passive duty statements triggers (Penalty P = -40)
DUTY_STATEMENT_PATTERNS = [
    r'^(?:responsible for|assisted in|helped to|helped with|worked on|tasked with|participated in|involved in|handled|supported)\b',
    r'\b(?:duties included|responsibilities were)\b'
]

# Quantifiable metric patterns (Weight w_Y = 0.45)
METRIC_PATTERNS = [
    r'\b\d+(?:\.\d+)?%',                                                  # Percentages: 30%, 99.9%
    r'\$\s*\d+(?:,\d{3})*(?:\.\d+)?\s*(?:[kKmMbB]|thousand|million)?\b', # Currency: $50k, $1.2M
    r'\b\d+(?:\.\d+)?\s*(?:ms|milliseconds?|seconds?|mins?|minutes?|hours?|days?)\b', # Latency/time
    r'\b\d+(?:\.\d+)?\s*[xX]\b|\b\d+(?:\.\d+)?-fold\b',                  # Multipliers: 2x, 5-fold
    r'\b\d+(?:,\d{3})*(?:\+)?\s*(?:users|qps|rps|req/s|queries|nodes|clusters|endpoints|clients|records|events|rows|services|microservices|pipelines|tenants|customers)\b', # Scale
    r'\b\d+(?:,\d{3})*\b'                                                 # Generic standalone integers
]

# Technical tooling and methods (Weight w_Z = 0.30)
TECH_TOOLING_ONTOLOGY = {
    "python", "fastapi", "flask", "django", "react", "vue", "angular", "next.js",
    "typescript", "javascript", "node.js", "nodejs", "express", "go", "golang",
    "rust", "java", "c++", "c#", ".net", "docker", "kubernetes", "k8s", "helm",
    "terraform", "aws", "gcp", "azure", "cloud", "lambda", "s3", "ec2",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "kafka", "rabbitmq", "graphql", "rest", "grpc", "ci/cd", "github actions",
    "gitlab ci", "jenkins", "pytorch", "tensorflow", "scikit-learn", "llm",
    "gemini", "openai", "prometheus", "grafana", "microservices", "sql", "nosql"
}


def score_resume_bullet(bullet: str, seniority: Optional[str] = "mid") -> Dict[str, Any]:
    """
    Evaluates a resume bullet point using the deterministic Google/IBM X-Y-Z formula:
    'Accomplished [X] as measured by [Y], by doing [Z]'

    Calculated as:
        S_bullet = (w_X * S_X + w_Y * S_Y + w_Z * S_Z) - P

    Weights:
        w_X = 0.25 (Action Verb & Scope)
        w_Y = 0.45 (Quantifiable Metric & Business Outcome)
        w_Z = 0.30 (Method, Tooling & Architecture)
        P = Total Deductions

    :param bullet: Single resume bullet point text
    :param seniority: Seniority tier ('junior', 'mid', 'senior', 'staff')
    :return: Comprehensive audit dictionary with score (0-100), components, and tips
    """
    cleaned = bullet.strip().strip("•-* \t\n")
    words = cleaned.split()
    word_count = len(words)

    if not cleaned or word_count == 0:
        return {
            "score": 0,
            "tier": "Empty",
            "component_scores": {"action_score": 0, "metric_score": 0, "tooling_score": 0},
            "detected_action_verbs": [],
            "detected_metrics": [],
            "detected_tools": [],
            "penalties": [{"deduction": 100, "reason": "Empty bullet point."}],
            "improvement_tips": ["Provide a bullet point describing an accomplishment with measurable results."]
        }

    lower_bullet = cleaned.lower()
    first_word = words[0].lower().rstrip(",.:;")
    first_two_words = " ".join([w.lower().rstrip(",.:;") for w in words[:2]])

    penalties: List[Dict[str, Any]] = []
    improvement_tips: List[str] = []

    # 1. Action Verb Evaluation (S_X)
    is_passive_duty = any(re.search(pat, lower_bullet) for pat in DUTY_STATEMENT_PATTERNS)
    detected_verbs = []

    if is_passive_duty:
        action_score = 15
        penalties.append({
            "deduction": 40,
            "name": "Passive Duty Statement",
            "reason": "Bullet begins with passive phrasing (e.g. 'Responsible for', 'Assisted in')."
        })
        improvement_tips.append(
            "Replace passive duty statements with active verbs (e.g., 'Architected', 'Engineered', 'Optimized')."
        )
    elif first_word in POWER_ACTION_VERBS:
        action_score = 100
        detected_verbs.append(words[0])
    elif first_word in MEDIUM_ACTION_VERBS:
        action_score = 75
        detected_verbs.append(words[0])
    else:
        # Check if a power verb appears within the first 3 words
        found_verb = None
        for w in words[:3]:
            cw = w.lower().rstrip(",.:;")
            if cw in POWER_ACTION_VERBS:
                found_verb = w
                break
        if found_verb:
            action_score = 80
            detected_verbs.append(found_verb)
        else:
            action_score = 40
            improvement_tips.append(
                f"Start your bullet with a strong action verb (e.g. 'Architected', 'Spearheaded') instead of '{words[0]}'."
            )

    # 2. Metric & Business Outcome Evaluation (S_Y)
    detected_metrics = []
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, cleaned, flags=re.IGNORECASE)
        for m in matches:
            if m not in detected_metrics:
                detected_metrics.append(m)

    # Classify metric strength
    has_rich_metric = any(
        "%" in m or "$" in m or "x" in m.lower() or any(unit in m.lower() for unit in ["ms", "sec", "user", "qps", "req"])
        for m in detected_metrics
    )

    if has_rich_metric:
        metric_score = 100
    elif len(detected_metrics) > 0:
        metric_score = 70
    else:
        metric_score = 10
        improvement_tips.append(
            "Incorporate quantifiable metrics (e.g., '% improvement', '$ saved', 'latency reduction in ms')."
        )

    # 3. Tooling & Architecture Evaluation (S_Z)
    detected_tools = []
    for token in re.findall(r'[A-Za-z0-9\.\+#\-]+', lower_bullet):
        if token in TECH_TOOLING_ONTOLOGY and token not in detected_tools:
            detected_tools.append(token)

    if len(detected_tools) >= 2:
        tooling_score = 100
    elif len(detected_tools) == 1:
        tooling_score = 70
    else:
        tooling_score = 25
        improvement_tips.append(
            "Explicitly mention the core technologies, tools, or architectural frameworks used."
        )

    # 4. Length & Cognitive Overload Penalties
    if word_count > 38:
        penalties.append({
            "deduction": 25,
            "name": "Cognitive Overload / Verbosity",
            "reason": f"Bullet is {word_count} words long. Bullets over 35 words cause recruiter skim fatigue."
        })
        improvement_tips.append("Condense bullet to under 30 words for maximum impact.")
    elif word_count < 6:
        penalties.append({
            "deduction": 30,
            "name": "Under-Detailed Statement",
            "reason": f"Bullet is only {word_count} words long and lacks necessary context."
        })
        improvement_tips.append("Expand bullet with specific scope, technologies used, and outcomes achieved.")

    # 5. Calculate Weighted Score
    w_x, w_y, w_z = 0.25, 0.45, 0.30
    raw_score = (w_x * action_score) + (w_y * metric_score) + (w_z * tooling_score)
    total_deductions = sum(p["deduction"] for p in penalties)
    final_score = max(0, min(100, int(round(raw_score - total_deductions))))

    if final_score >= 85:
        tier = "Elite XYZ Impact"
    elif final_score >= 70:
        tier = "Strong Achievement"
    elif final_score >= 50:
        tier = "Acceptable / Needs Polish"
    else:
        tier = "Weak / Passive Phrasing"

    return {
        "score": final_score,
        "tier": tier,
        "word_count": word_count,
        "component_scores": {
            "action_score": action_score,
            "metric_score": metric_score,
            "tooling_score": tooling_score
        },
        "detected_action_verbs": detected_verbs,
        "detected_metrics": detected_metrics,
        "detected_tools": detected_tools,
        "penalties": penalties,
        "improvement_tips": improvement_tips
    }
