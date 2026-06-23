"""
Wiki router: pages listing, page detail, and overview statistics.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import Concept
from app.services.data_store import store

router = APIRouter(prefix="/api/wiki", tags=["wiki"])


@router.get("/pages")
async def list_pages() -> list[Concept]:
    """List all wiki pages (concepts)."""
    return store.get_concepts()


@router.get("/pages/{page_id}")
async def get_page(page_id: str) -> Concept:
    """Get a specific wiki page by its page_id."""
    concepts = store.get_concepts()
    concept = next((c for c in concepts if c.page_id == page_id), None)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Page '{page_id}' not found")
    return concept


@router.get("/overview")
async def get_overview() -> dict:
    """Get an overview of the wiki knowledge base."""
    sources = store.get_sources()
    claims = store.get_claims()
    concepts = store.get_concepts()
    graph = store.get_graph()
    aliases = store.get_aliases()
    tests = store.get_tests()

    return {
        "total_sources": len(sources),
        "total_claims": len(claims),
        "total_pages": len(concepts),
        "total_graph_nodes": len(graph.nodes),
        "total_graph_edges": len(graph.edges),
        "total_aliases": len(aliases),
        "total_tests": len(tests),
        "rounds_available": store.get_round_names(),
    }
