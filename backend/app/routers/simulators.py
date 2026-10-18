import logging
from fastapi import APIRouter, HTTPException, Request

from app.limiter import limiter
from app.ats_simulator import run_multi_ats_simulation
from app.ats_benchmarker import benchmark_ats_parsing_resilience
from app.simulators import (
    simulate_workday_parsing,
    simulate_greenhouse_parsing,
    simulate_taleo_parsing,
    simulate_icims_parsing,
    simulate_lever_parsing,
    simulate_successfactors_parsing
)
from app.schemas import SimulateATSRequest, AtsSimulatorRequest, ATSBenchmarkRequest

router = APIRouter(tags=["Multi-ATS Simulation Sandbox"])
logger = logging.getLogger("ResumeAnalyserAPI.Simulators")


@router.post("/api/simulate-ats")
@limiter.limit("30/minute")
def simulate_ats_endpoint(request: Request, payload: SimulateATSRequest):
    """
    Simulates parsing behavior across Workday, Greenhouse/Lever, and Taleo/Oracle ATS engines,
    providing comparative diffs, entity extraction health, and cross-ATS hazard alerts.
    """
    try:
        result = run_multi_ats_simulation(payload.resume_text)
        return result
    except Exception as err:
        logger.error(f"Error in simulate ATS endpoint: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate ATS parsing: {str(err)}")


@router.post("/api/simulate/ats")
@limiter.limit("60/minute")
def simulate_multi_ats_endpoint(request: Request, payload: AtsSimulatorRequest):
    """
    Executes composite multi-ATS parser emulation across Workday, Greenhouse, Taleo, and iCIMS.
    """
    try:
        return run_multi_ats_simulation(payload.resume_text)
    except Exception as err:
        logger.error(f"Error executing multi-ATS simulation: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate multi-ATS parsing: {str(err)}")


@router.post("/api/simulate/icims")
@limiter.limit("60/minute")
def simulate_icims_endpoint(request: Request, payload: AtsSimulatorRequest):
    """
    Simulates iCIMS Enterprise Talent Cloud parsing heuristics and hazard identification.
    """
    try:
        return simulate_icims_parsing(payload.resume_text)
    except Exception as err:
        logger.error(f"Error simulating iCIMS parsing: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate iCIMS: {str(err)}")


@router.post("/api/simulate/workday")
@limiter.limit("60/minute")
def simulate_workday_endpoint(request: Request, payload: AtsSimulatorRequest):
    """
    Simulates Workday parsing heuristics.
    """
    try:
        return simulate_workday_parsing(payload.resume_text)
    except Exception as err:
        logger.error(f"Error simulating Workday parsing: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate Workday: {str(err)}")


@router.post("/api/simulate/greenhouse")
@limiter.limit("60/minute")
def simulate_greenhouse_endpoint(request: Request, payload: AtsSimulatorRequest):
    """
    Simulates Greenhouse / Lever parsing heuristics.
    """
    try:
        return simulate_greenhouse_parsing(payload.resume_text)
    except Exception as err:
        logger.error(f"Error simulating Greenhouse parsing: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate Greenhouse: {str(err)}")


@router.post("/api/simulate/taleo")
@limiter.limit("60/minute")
def simulate_taleo_endpoint(request: Request, payload: AtsSimulatorRequest):
    """
    Simulates Taleo / Oracle ATS parsing heuristics.
    """
    try:
        return simulate_taleo_parsing(payload.resume_text)
    except Exception as err:
        logger.error(f"Error simulating Taleo parsing: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate Taleo: {str(err)}")


@router.post("/api/simulate/lever")
@limiter.limit("60/minute")
def simulate_lever_endpoint(request: Request, payload: AtsSimulatorRequest):
    """
    Simulates Lever ATS plain-text linearization and candidate fast-tagging.
    """
    try:
        return simulate_lever_parsing(payload.resume_text)
    except Exception as err:
        logger.error(f"Error simulating Lever parsing: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate Lever: {str(err)}")


@router.post("/api/simulate/successfactors")
@limiter.limit("60/minute")
def simulate_successfactors_endpoint(request: Request, payload: AtsSimulatorRequest):
    """
    Simulates SAP SuccessFactors XML candidate profile mapping and delimiter conformance.
    """
    try:
        return simulate_successfactors_parsing(payload.resume_text)
    except Exception as err:
        logger.error(f"Error simulating SAP SuccessFactors parsing: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate SAP SuccessFactors: {str(err)}")


@router.post("/api/audit/ats-benchmark")
@router.post("/api/ats-benchmark")
@limiter.limit("60/minute")
def benchmark_ats_parsing_endpoint(request: Request, payload: ATSBenchmarkRequest):
    """
    Evaluates resume against multi-engine parsing failure modes across Workday,
    Taleo, Greenhouse, and iCIMS.
    """
    try:
        return benchmark_ats_parsing_resilience(payload.resume_text)
    except Exception as err:
        logger.error(f"Error executing ATS parsing benchmark: {err}")
        raise HTTPException(status_code=500, detail=f"Failed to benchmark ATS resilience: {str(err)}")
