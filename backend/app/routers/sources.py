"""
Sources router: CRUD and demo loading for knowledge sources.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import Source
from app.services.data_store import store

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("")
async def list_sources() -> list[Source]:
    """List all sources in the knowledge base."""
    return store.get_sources()


@router.post("/load-demo")
async def load_demo() -> dict:
    """
    Load demo source data.
    (In production this would trigger a data loading pipeline.
    For now, returns info about currently loaded data.)
    """
    sources = store.get_sources()
    return {
        "message": "Demo data loaded (data is loaded from workspace/index/ on startup).",
        "source_count": len(sources),
    }


@router.get("/{source_id}")
async def get_source(source_id: str) -> Source:
    """Get a specific source by ID."""
    sources = store.get_sources()
    source = next((s for s in sources if s.source_id == source_id), None)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")
    return source
