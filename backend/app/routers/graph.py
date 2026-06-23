"""
Graph router: knowledge graph, provenance graph, and failure graph endpoints.
"""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import LinkGraph
from app.services.data_store import store
from app.services.graph import graph_service

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/knowledge")
async def get_knowledge_graph(
    round_name: str = Query(default="", description="Round name"),
    issue_type: str = Query(default="", description="Filter by issue type"),
) -> LinkGraph:
    """Get the knowledge graph for a given round, optionally filtered by issue type."""
    rounds = store.get_round_names()
    if not rounds:
        return LinkGraph()

    if not round_name:
        round_name = rounds[-1]

    return graph_service.get_knowledge_graph(round_name, issue_type if issue_type else None)


@router.get("/provenance")
async def get_provenance_graph(claim_id: str = Query(..., description="Claim ID")) -> LinkGraph:
    """Get the provenance graph for a specific claim (Source -> Claim -> Page)."""
    graph = graph_service.get_provenance_graph(claim_id)
    if not graph.nodes:
        raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found")
    return graph


@router.get("/failure")
async def get_failure_graph(query_id: str = Query(..., description="Query ID")) -> LinkGraph:
    """Get a graph highlighting expected vs retrieved pages for a query."""
    graph = graph_service.get_failure_graph(query_id)
    if not graph.nodes:
        raise HTTPException(status_code=404, detail=f"Query '{query_id}' not found or no data available")
    return graph
