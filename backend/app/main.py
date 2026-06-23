"""
AgentKB-Diag Backend — FastAPI application.

A diagnostic system for wiki knowledge bases maintained by LLM agents.
Provides health metrics, issue detection, retrieval evaluation, and graph
visualization for knowledge bases across multiple experiment rounds.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import sources, wiki, diagnosis, retrieval, graph, experiment, pipeline

app = FastAPI(
    title="AgentKB-Diag API",
    description="Diagnostic system for LLM-agent-managed wiki knowledge bases",
    version="1.0.0",
)

# CORS — allow Vite dev server on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(sources.router)
app.include_router(wiki.router)
app.include_router(diagnosis.router)
app.include_router(retrieval.router)
app.include_router(graph.router)
app.include_router(experiment.router)
app.include_router(pipeline.router)


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "AgentKB-Diag Backend"}


@app.get("/")
async def root() -> dict:
    """Root endpoint with API overview."""
    return {
        "name": "AgentKB-Diag API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /api/health",
            "sources": {
                "list": "GET /api/sources",
                "load_demo": "POST /api/sources/load-demo",
                "detail": "GET /api/sources/{source_id}",
            },
            "wiki": {
                "pages": "GET /api/wiki/pages",
                "page_detail": "GET /api/wiki/pages/{page_id}",
                "overview": "GET /api/wiki/overview",
            },
            "diagnosis": {
                "run": "POST /api/diagnosis/run?round_name=",
                "summary": "GET /api/diagnosis/summary?round_name=",
                "issues": "GET /api/diagnosis/issues?round_name=&issue_type=&severity=",
                "issue_detail": "GET /api/diagnosis/issues/{issue_id}?round_name=",
            },
            "retrieval": {
                "search": "POST /api/retrieval/search",
                "evaluate": "POST /api/retrieval/evaluate?round_name=",
                "failures": "GET /api/retrieval/failures?round_name=&query_id=",
            },
            "graph": {
                "knowledge": "GET /api/graph/knowledge?round_name=&issue_type=",
                "provenance": "GET /api/graph/provenance?claim_id=",
                "failure": "GET /api/graph/failure?query_id=",
            },
            "experiments": {
                "run_round": "POST /api/experiments/run-round",
                "metrics": "GET /api/experiments/metrics",
                "export": "GET /api/experiments/export?format=csv|json",
            },
            "pipeline": {
                "build": "POST /api/pipeline/build?round_name=&mode=",
                "status": "GET /api/pipeline/status",
                "agent_ask": "POST /api/pipeline/agent/ask",
                "agent_health": "GET /api/pipeline/agent/health",
            },
        },
    }
