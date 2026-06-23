"""
Pipeline router: agent pipeline execution, status, and diagnostic agent ask.
"""

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.agent_harness import (
    AgentHarness,
    create_harness_from_settings,
    _slugify,
)
from app.services.agent_logger import AgentLogger
from app.services.data_store import store

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class AgentQueryRequest(BaseModel):
    question: str
    round_name: str = ""


class AgentQueryResponse(BaseModel):
    answer: str
    sources: list[str] = []


class PipelineStatusResponse(BaseModel):
    mode: str
    rounds_available: list[str]
    recent_logs: list[str]


class BuildRoundRequest(BaseModel):
    round_name: str = "round_1"
    mode: str = "rule"
    sources: list[dict] = []


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent  # backend/app/routers -> project root


def _sources_dir() -> Path:
    return _project_root() / "data" / "converted"


def _rounds_dir() -> Path:
    return _project_root() / "workspace" / "rounds"


def _index_dir() -> Path:
    return _project_root() / "workspace" / "index"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/build", response_model=dict)
async def build_round(
    round_name: str = Query(..., description="Round name, e.g. round_1, round_2, round_3"),
    mode: str = Query(default="rule", description="Execution mode: rule or llm"),
):
    """Run the full agent pipeline for a round.

    Loads source documents from data/converted/<round_name>/, runs the 7-agent
    pipeline on each, and saves generated wiki pages, claims, concepts, and
    links to workspace/rounds/<round_name>/ and workspace/index/.
    """
    round_dir = _sources_dir() / round_name
    if not round_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Source directory not found: {round_dir}. Place .md or .txt files in data/converted/{round_name}/",
        )

    # Load source files
    sources: list[dict] = []
    for fpath in sorted(round_dir.glob("*")):
        if fpath.suffix.lower() in (".md", ".txt"):
            text = fpath.read_text(encoding="utf-8")
            source_id = fpath.stem
            sources.append({"text": text, "source_id": source_id})

    if not sources:
        raise HTTPException(
            status_code=400,
            detail=f"No .md or .txt files found in {round_dir}",
        )

    # Determine round number from name
    try:
        round_num = int(round_name.split("_")[-1])
    except (ValueError, IndexError):
        round_num = 1

    # Run pipeline
    harness = create_harness_from_settings()
    harness.config.mode = mode  # type: ignore[assignment]

    result = await harness.run_pipeline_batch(sources, round_num=round_num, mode=mode)

    # Save results
    out_dir = _rounds_dir() / round_name
    out_dir.mkdir(parents=True, exist_ok=True)
    index_dir = _index_dir()
    index_dir.mkdir(parents=True, exist_ok=True)

    # Save concepts
    concepts_data = [
        {
            "concept_id": f"CON-{round_num:03d}-{i:03d}",
            "canonical_name": c.canonical_name,
            "aliases": c.aliases,
            "definition": c.definition,
            "page_id": f"concept_{c.canonical_name.lower().replace(' ', '_')}",
            "round_created": round_num,
            "round_updated": round_num,
        }
        for i, c in enumerate(result.concepts)
    ]
    _write_json(out_dir / "concepts.json", concepts_data)
    _write_json(index_dir / "concepts.json", concepts_data)

    # Save claims. Infer page_id by matching claim text against concept names
    # (rule mode does not carry explicit claim→concept attribution; this is a
    # best-effort heuristic that prevents the legacy "page_id always empty" bug).
    concept_names = {c.canonical_name.lower(): c.canonical_name for c in result.concepts}
    concept_slugs = {_slugify(c.canonical_name).lower(): c.canonical_name for c in result.concepts}

    def _infer_claim_page_id(claim_text: str) -> str:
        text_lower = claim_text.lower()
        for name in sorted(concept_names, key=len, reverse=True):
            if name in text_lower:
                return _slugify(concept_names[name])
        for slug in sorted(concept_slugs, key=len, reverse=True):
            if slug in text_lower:
                return _slugify(concept_slugs[slug])
        return ""

    claims_data = [
        {
            "claim_id": c.claim_id,
            "text": c.text,
            "page_id": _infer_claim_page_id(c.text),
            "source_ids": c.source_ids,
            "round_created": round_num,
            "round_updated": round_num,
            "status": c.status,
        }
        for c in result.claims
    ]
    _write_json(out_dir / "claims.json", claims_data)
    _write_json(index_dir / "claims.json", claims_data)

    # Save wiki pages
    pages_data = [
        {
            "page_id": p.page_id,
            "title": p.title,
            "content": p.content,
            "type": p.page_type,
            "tags": p.tags,
            "round": round_num,
        }
        for p in result.wiki_pages
    ]
    _write_json(out_dir / "wiki_pages.json", pages_data)

    # Save graph (links)
    graph_data = {
        "nodes": [
            {
                "id": p.page_id,
                "type": p.page_type,
                "label": p.title,
                "round_created": round_num,
                "issue_flags": [],
            }
            for p in result.wiki_pages
        ],
        "edges": [
            {
                "source": l.source_page_id,
                "target": l.target_page_id,
                "type": l.link_type,
                "round_created": round_num,
                "confidence": l.confidence,
            }
            for l in result.links
        ],
    }
    _write_json(out_dir / "graph.json", graph_data)
    _write_json(index_dir / "graph.json", graph_data)

    # Save sources index
    sources_data = [
        {
            "source_id": s.source_id,
            "title": s.title,
            "authors": s.authors,
            "year": s.year,
            "round": round_num,
            "tags": s.tags,
            "path": f"data/converted/{round_name}/{s.source_id}.md",
        }
        for s in result.sources
    ]
    _write_json(out_dir / "sources.json", sources_data)
    _write_json(index_dir / "sources.json", sources_data)

    # Also write Markdown pages to workspace/wiki/ in OKF directory layout
    # (concepts/, sources/, syntheses/). Content already includes frontmatter.
    wiki_dir = _project_root() / "workspace" / "wiki"
    for subdir in ("concepts", "sources", "syntheses"):
        (wiki_dir / subdir).mkdir(parents=True, exist_ok=True)
    for page in result.wiki_pages:
        # page.page_id is prefixed "concept_<slug>" or "source_<sid>"; split
        # into OKF subdirectory + filename.
        if page.page_id.startswith("concept_"):
            fname = page.page_id[len("concept_"):]
            subdir = "concepts"
        elif page.page_id.startswith("source_"):
            fname = page.page_id[len("source_"):]
            subdir = "sources"
        else:
            fname = page.page_id
            subdir = "syntheses"
        md_path = wiki_dir / subdir / f"{fname}.md"
        md_path.write_text(page.content, encoding="utf-8")

    return {
        "status": "completed",
        "round_name": round_name,
        "mode": mode,
        "sources_processed": len(sources),
        "concepts_extracted": len(result.concepts),
        "claims_extracted": len(result.claims),
        "wiki_pages_generated": len(result.wiki_pages),
        "links_detected": len(result.links),
        "errors": result.errors,
    }


@router.get("/status", response_model=PipelineStatusResponse)
async def pipeline_status():
    """Get current pipeline status and recent agent logs."""
    logger = AgentLogger()
    recent_logs = logger.get_recent(30)

    return PipelineStatusResponse(
        mode="rule",
        rounds_available=store.get_round_names(),
        recent_logs=recent_logs,
    )


@router.post("/agent/ask", response_model=AgentQueryResponse)
async def ask_agent(request: AgentQueryRequest):
    """Ask the diagnostic agent a question about the knowledge base.

    Analyzes current KB state (metrics, issues, graph) and returns a
    diagnostic answer with cited sources.
    """
    harness = create_harness_from_settings()

    # Gather KB context for the diagnostic agent
    round_name = request.round_name or "round_3"

    # Get metrics if available
    metrics = {}
    try:
        metrics_snapshot = store.get_round_snapshot(round_name, "diagnosis.json")
        if isinstance(metrics_snapshot, dict) and "metrics" in metrics_snapshot:
            metrics = metrics_snapshot["metrics"]
        elif isinstance(metrics_snapshot, dict):
            metrics = metrics_snapshot
    except Exception:
        pass

    # Get issues
    issues: list[dict] = []
    try:
        issues_snapshot = store.get_round_snapshot(round_name, "issues.json")
        if isinstance(issues_snapshot, list):
            issues = issues_snapshot
    except Exception:
        pass

    # Get graph stats
    graph = store.get_round_graph(round_name)
    graph_stats = {
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "orphan_count": sum(1 for n in graph.nodes if "orphan" in n.issue_flags),
        "duplicate_count": sum(1 for n in graph.nodes if "duplicate" in n.issue_flags),
    }

    kb_context = {
        "round_name": round_name,
        "metrics": metrics,
        "issues": issues,
        "graph_stats": graph_stats,
    }

    result = await harness.ask_diagnostic_agent(request.question, kb_context)
    return AgentQueryResponse(
        answer=result.get("answer", "I could not analyze the knowledge base. Please check that data is loaded."),
        sources=result.get("sources", []),
    )


@router.get("/agent/health")
async def agent_health() -> dict:
    """Check if the agent harness is operational."""
    harness = create_harness_from_settings()
    return {
        "status": "ok",
        "mode": harness.config.mode.value if hasattr(harness.config.mode, "value") else harness.config.mode,
        "provider": harness.config.provider,
        "model": harness.config.model,
        "llm_configured": bool(harness.config.api_key),
        "rule_mode_available": True,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_json(path: Path, data: object) -> None:
    """Write JSON data to path, ensuring parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
