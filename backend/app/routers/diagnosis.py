"""
Diagnosis router: run health checks, get summary, and list/filter issues.
"""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import HealthReport, Issue
from app.services.data_store import store
from app.services.diagnosis import diagnosis_service

router = APIRouter(prefix="/api/diagnosis", tags=["diagnosis"])


@router.post("/run")
async def run_diagnosis(round_name: str = Query(default="", description="Round name to diagnose")) -> HealthReport:
    """Run diagnosis for a given round (or latest available round)."""
    rounds = store.get_round_names()
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds available for diagnosis")

    if not round_name:
        round_name = rounds[-1]
    elif round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    report = diagnosis_service.compute_all_metrics(round_name)
    return report


@router.get("/summary")
async def get_summary(round_name: str = Query(default="", description="Round name for summary")) -> HealthReport:
    """Get the health summary for a round (or latest available round)."""
    rounds = store.get_round_names()
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds available")

    if not round_name:
        round_name = rounds[-1]
    elif round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    report = diagnosis_service.compute_all_metrics(round_name)
    return report


@router.get("/issues")
async def list_issues(
    round_name: str = Query(default="", description="Round name"),
    issue_type: str = Query(default="", description="Filter by issue type"),
    severity: str = Query(default="", description="Filter by severity"),
) -> list[Issue]:
    """List all issues found in a round, with optional filtering."""
    rounds = store.get_round_names()
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds available")

    if not round_name:
        round_name = rounds[-1]
    elif round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    issues = diagnosis_service.find_issues(round_name)

    if issue_type:
        issues = [i for i in issues if i.type == issue_type]
    if severity:
        issues = [i for i in issues if i.severity == severity]

    return issues


@router.get("/issues/{issue_id}")
async def get_issue(issue_id: str, round_name: str = Query(default="", description="Round name")) -> Issue:
    """Get a specific issue by its ID."""
    rounds = store.get_round_names()
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds available")

    if not round_name:
        round_name = rounds[-1]
    elif round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    issues = diagnosis_service.find_issues(round_name)
    issue = next((i for i in issues if i.issue_id == issue_id), None)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found")

    return issue
