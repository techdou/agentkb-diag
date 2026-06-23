"""
Experiment router: run round experiments, view metrics comparison,
method comparison, case studies, and export data.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.models.schemas import (
    HealthReport,
    MethodComparison,
    CaseStudy,
    RoundResult,
)
from app.services.data_store import store
from app.services.experiment import experiment_service

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


class RunRoundRequest:
    """Request model for running a full experiment round."""
    def __init__(self, round_name: str):
        self.round_name = round_name


from pydantic import BaseModel as PydanticBase


class RunRoundReq(PydanticBase):
    round_name: str


# ── Existing endpoints ──────────────────────────────────────────

@router.post("/run-round")
async def run_round(request: RunRoundReq) -> RoundResult:
    """Run full diagnosis pipeline for a specific round."""
    rounds = store.get_round_names()
    if request.round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{request.round_name}' not found")

    result = experiment_service.run_full_round(request.round_name)
    return result


@router.get("/metrics")
async def get_metrics() -> list[HealthReport]:
    """Get health metrics for all available rounds for comparison."""
    return experiment_service.get_metrics()


@router.get("/export", response_class=PlainTextResponse)
async def export_data(format: str = Query(default="csv", description="Export format: csv or json")) -> str:
    """Export all rounds' metrics in CSV or JSON format."""
    if format == "json":
        return experiment_service.export_json()
    return experiment_service.export_csv()


# ── New endpoints ───────────────────────────────────────────────

@router.get("/method-comparison")
async def method_comparison(round_name: str = Query(..., description="Round name to compare methods on")) -> MethodComparison:
    """
    Run all 4 retrieval methods against the given round and return
    per-method Recall@3, MRR, and per-query breakdown.
    """
    rounds = store.get_round_names()
    if round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    return experiment_service.run_method_comparison(round_name)


@router.get("/cases")
async def get_cases() -> list[CaseStudy]:
    """Return the 4 paper-level case studies with narrative text."""
    return experiment_service.get_case_studies()


@router.get("/full-comparison")
async def full_comparison() -> list[dict]:
    """Get method comparison data across all rounds x all 4 methods."""
    return experiment_service.get_full_comparison()
