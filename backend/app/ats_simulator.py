from typing import Dict, Any, List
from app.simulators.workday import simulate_workday_parsing
from app.simulators.greenhouse import simulate_greenhouse_parsing
from app.simulators.taleo import simulate_taleo_parsing

def run_multi_ats_simulation(resume_text: str) -> Dict[str, Any]:
    """
    Executes multi-ATS parser emulation across Workday, Greenhouse/Lever, and Taleo/Oracle.
    Computes unified cross-ATS compatibility scores and identifies high-risk parser discrepancies.
    """
    if not resume_text or not resume_text.strip():
        return {
            "overall_cross_ats_score": 0,
            "tier": "Empty Document",
            "engines": {
                "workday": simulate_workday_parsing(""),
                "greenhouse": simulate_greenhouse_parsing(""),
                "taleo": simulate_taleo_parsing("")
            },
            "summary_alerts": ["No text provided for ATS simulation."]
        }

    workday_res = simulate_workday_parsing(resume_text)
    greenhouse_res = simulate_greenhouse_parsing(resume_text)
    taleo_res = simulate_taleo_parsing(resume_text)

    # Calculate weighted composite score
    overall_score = round(
        (workday_res["compatibility_score"] * 0.4) +
        (greenhouse_res["compatibility_score"] * 0.35) +
        (taleo_res["compatibility_score"] * 0.25)
    )

    if overall_score >= 85:
        tier = "Universal ATS Compatible (Low Risk)"
    elif overall_score >= 70:
        tier = "Moderate Risk (Some ATS Quirks Detected)"
    else:
        tier = "High Formatting Risk (Potential Parsing Failures)"

    # Aggregate high priority alerts
    all_alerts = []
    for eng in [workday_res, greenhouse_res, taleo_res]:
        for h in eng.get("hazards", []):
            all_alerts.append(f"[{eng['engine']}] {h}")

    return {
        "overall_cross_ats_score": overall_score,
        "tier": tier,
        "engines": {
            "workday": workday_res,
            "greenhouse": greenhouse_res,
            "taleo": taleo_res
        },
        "summary_alerts": all_alerts
    }
