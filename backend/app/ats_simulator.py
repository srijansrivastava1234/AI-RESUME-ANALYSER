from typing import Dict, Any, List
from app.simulators.workday import simulate_workday_parsing
from app.simulators.greenhouse import simulate_greenhouse_parsing
from app.simulators.taleo import simulate_taleo_parsing
from app.simulators.icims import simulate_icims_parsing
from app.simulators.lever import simulate_lever_parsing
from app.simulators.successfactors import simulate_successfactors_parsing

def run_multi_ats_simulation(resume_text: str) -> Dict[str, Any]:
    """
    Executes multi-ATS parser emulation across Workday, Greenhouse, Taleo, iCIMS, Lever, and SAP SuccessFactors.
    Computes unified cross-ATS compatibility scores and identifies high-risk parser discrepancies.
    """
    if not resume_text or not resume_text.strip():
        return {
            "overall_cross_ats_score": 0,
            "tier": "Empty Document",
            "engines": {
                "workday": simulate_workday_parsing(""),
                "greenhouse": simulate_greenhouse_parsing(""),
                "taleo": simulate_taleo_parsing(""),
                "icims": simulate_icims_parsing(""),
                "lever": simulate_lever_parsing(""),
                "successfactors": simulate_successfactors_parsing("")
            },
            "summary_alerts": ["No text provided for ATS simulation."]
        }

    workday_res = simulate_workday_parsing(resume_text)
    greenhouse_res = simulate_greenhouse_parsing(resume_text)
    taleo_res = simulate_taleo_parsing(resume_text)
    icims_res = simulate_icims_parsing(resume_text)
    lever_res = simulate_lever_parsing(resume_text)
    successfactors_res = simulate_successfactors_parsing(resume_text)

    # Calculate weighted composite score across 6 top enterprise ATS engines
    overall_score = round(
        (workday_res["compatibility_score"] * 0.25) +
        (greenhouse_res["compatibility_score"] * 0.20) +
        (taleo_res["compatibility_score"] * 0.15) +
        (icims_res["compatibility_score"] * 0.15) +
        (lever_res["compatibility_score"] * 0.15) +
        (successfactors_res["compatibility_score"] * 0.10)
    )

    if overall_score >= 85:
        tier = "Universal ATS Compatible (Low Risk)"
    elif overall_score >= 70:
        tier = "Moderate Risk (Some ATS Quirks Detected)"
    else:
        tier = "High Formatting Risk (Potential Parsing Failures)"

    # Aggregate high priority alerts
    all_alerts = []
    for eng in [workday_res, greenhouse_res, taleo_res, icims_res, lever_res, successfactors_res]:
        for h in eng.get("hazards", []):
            all_alerts.append(f"[{eng['engine']}] {h}")

    return {
        "overall_cross_ats_score": overall_score,
        "tier": tier,
        "engines": {
            "workday": workday_res,
            "greenhouse": greenhouse_res,
            "taleo": taleo_res,
            "icims": icims_res,
            "lever": lever_res,
            "successfactors": successfactors_res
        },
        "summary_alerts": all_alerts
    }
