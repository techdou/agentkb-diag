"""
Retrieval router: search queries, evaluate retrieval performance, and failure analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.schemas import SearchResult, RetrievalResult, FailureAttribution
from app.services.data_store import store
from app.services.retrieval import retrieval_service

router = APIRouter(prefix="/api/retrieval", tags=["retrieval"])


class SearchRequest(BaseModel):
    query: str
    round_name: str = ""
    top_k: int = 5


@router.post("/search")
async def search(request: SearchRequest) -> list[SearchResult]:
    """Search the knowledge base for pages relevant to the query."""
    rounds = store.get_round_names()
    if not rounds:
        return []

    round_name = request.round_name if request.round_name else rounds[-1]
    if round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    results = retrieval_service.search(request.query, round_name, top_k=request.top_k)
    return results


@router.post("/evaluate")
async def evaluate(round_name: str = Query(default="", description="Round name to evaluate")) -> list[RetrievalResult]:
    """Run all retrieval tests and evaluate performance for a given round."""
    rounds = store.get_round_names()
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds available")

    if not round_name:
        round_name = rounds[-1]
    elif round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    results = retrieval_service.evaluate(round_name)
    return results


@router.get("/failures")
async def get_failures(
    round_name: str = Query(default="", description="Round name"),
    query_id: str = Query(default="", description="Filter by query ID"),
) -> list[RetrievalResult]:
    """Get retrieval evaluation results with failure information."""
    rounds = store.get_round_names()
    if not rounds:
        raise HTTPException(status_code=404, detail="No rounds available")

    if not round_name:
        round_name = rounds[-1]
    elif round_name not in rounds:
        raise HTTPException(status_code=404, detail=f"Round '{round_name}' not found")

    results = retrieval_service.evaluate(round_name)

    # Filter only failed results, optionally by query_id
    failures = [r for r in results if not r.all_hit]
    if query_id:
        failures = [r for r in failures if r.query_id == query_id]

    return failures
