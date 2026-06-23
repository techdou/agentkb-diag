"""
Data store singleton that loads all JSON data from workspace/index/ and workspace/rounds/
on startup. Provides access to sources, claims, concepts, graph, aliases, and tests.

OKF relationship: the canonical knowledge source is the OKF v0.1 bundle at the
project root (`okf/`). The JSON files in workspace/index/ are *derived* from
that bundle via backend/scripts/okf_import.py. This store reads the derived
JSON for performance and decoupling — it does not parse OKF markdown at
runtime. Use `is_okf_stale()` to detect when the bundle has been edited and
the index JSON should be regenerated.
"""

import json
import os
import glob
from pathlib import Path
from typing import Optional

from app.models.schemas import (
    Source,
    Claim,
    Concept,
    LinkGraph,
    GraphNode,
    GraphEdge,
    AliasEntry,
    RetrievalTest,
)


# Compute the project root: backend/ => project root is parent of backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
PROJECT_ROOT = BACKEND_DIR.parent  # agentkb-diag/
INDEX_DIR = PROJECT_ROOT / "workspace" / "index"
ROUNDS_DIR = PROJECT_ROOT / "workspace" / "rounds"
OKF_DIR = PROJECT_ROOT / "okf"


# JSON index/snapshot files whose top-level structure is an object (dict).
# Everything else is a list. Used to return the correct empty value on failure.
_DICT_FILES = {"graph.json"}


def _load_json(rel_path: str) -> dict | list:
    """Load a JSON file relative to INDEX_DIR. Returns empty dict/list on failure."""
    path = INDEX_DIR / rel_path
    empty = {} if rel_path in _DICT_FILES else []
    if not path.exists():
        return empty
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return empty


def _load_round_snapshot(round_name: str, filename: str) -> dict | list:
    """Load a JSON snapshot file from a specific round directory."""
    path = ROUNDS_DIR / round_name / filename
    empty = {} if filename in _DICT_FILES else []
    if not path.exists():
        return empty
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return empty


class DataStore:
    """Singleton data store that caches all workspace data in memory."""

    _instance: Optional["DataStore"] = None

    def __new__(cls) -> "DataStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        # Index data
        self._sources: list[Source] = []
        self._claims: list[Claim] = []
        self._concepts: list[Concept] = []
        self._graph: LinkGraph = LinkGraph()
        self._aliases: list[AliasEntry] = []
        self._tests: list[RetrievalTest] = []

        # Round snapshots cache: round_name -> {filename: data}
        self._round_snapshots: dict[str, dict[str, dict | list]] = {}

        self._load_all()

    def _load_all(self) -> None:
        """Load all index data and round snapshots."""
        # Load index data
        raw_sources = _load_json("sources.json")
        self._sources = [Source(**s) for s in raw_sources] if isinstance(raw_sources, list) else []

        raw_claims = _load_json("claims.json")
        self._claims = [Claim(**c) for c in raw_claims] if isinstance(raw_claims, list) else []

        raw_concepts = _load_json("concepts.json")
        self._concepts = [Concept(**c) for c in raw_concepts] if isinstance(raw_concepts, list) else []

        raw_graph = _load_json("graph.json")
        if isinstance(raw_graph, dict):
            self._graph = LinkGraph(
                nodes=[GraphNode(**n) for n in raw_graph.get("nodes", [])],
                edges=[GraphEdge(**e) for e in raw_graph.get("edges", [])],
            )

        raw_aliases = _load_json("aliases.json")
        self._aliases = [AliasEntry(**a) for a in raw_aliases] if isinstance(raw_aliases, list) else []

        raw_tests = _load_json("retrieval_tests.json")
        self._tests = [RetrievalTest(**t) for t in raw_tests] if isinstance(raw_tests, list) else []

        # Load round snapshots
        if ROUNDS_DIR.exists():
            for round_dir in sorted(ROUNDS_DIR.iterdir()):
                if round_dir.is_dir():
                    round_name = round_dir.name
                    snapshots: dict[str, dict | list] = {}
                    for json_file in glob.glob(str(round_dir / "*.json")):
                        fname = Path(json_file).name
                        try:
                            with open(json_file, "r", encoding="utf-8") as f:
                                snapshots[fname] = json.load(f)
                        except (json.JSONDecodeError, OSError):
                            snapshots[fname] = {}
                    self._round_snapshots[round_name] = snapshots

    # ---- Public accessors ----

    def get_sources(self) -> list[Source]:
        return self._sources

    def get_claims(self) -> list[Claim]:
        return self._claims

    def get_concepts(self) -> list[Concept]:
        return self._concepts

    def get_graph(self) -> LinkGraph:
        return self._graph

    def get_aliases(self) -> list[AliasEntry]:
        return self._aliases

    def get_tests(self) -> list[RetrievalTest]:
        return self._tests

    def get_round_names(self) -> list[str]:
        """Return sorted list of available round names."""
        return sorted(self._round_snapshots.keys())

    def get_round_snapshot(self, round_name: str, filename: str) -> dict | list:
        """Get a specific snapshot from a round. Fall back to index data."""
        snapshots = self._round_snapshots.get(round_name, {})
        if filename in snapshots:
            return snapshots[filename]
        # Fallback to current index
        return _load_json(filename)

    def get_round_claims(self, round_name: str) -> list[Claim]:
        data = self.get_round_snapshot(round_name, "claims.json")
        if isinstance(data, list):
            return [Claim(**c) for c in data]
        return self._claims

    def get_round_sources(self, round_name: str) -> list[Source]:
        data = self.get_round_snapshot(round_name, "sources.json")
        if isinstance(data, list):
            return [Source(**s) for s in data]
        return self._sources

    def get_round_graph(self, round_name: str) -> LinkGraph:
        data = self.get_round_snapshot(round_name, "graph.json")
        if isinstance(data, dict):
            return LinkGraph(
                nodes=[GraphNode(**n) for n in data.get("nodes", [])],
                edges=[GraphEdge(**e) for e in data.get("edges", [])],
            )
        return self._graph

    def get_round_concepts(self, round_name: str) -> list[Concept]:
        data = self.get_round_snapshot(round_name, "concepts.json")
        if isinstance(data, list):
            return [Concept(**c) for c in data]
        return self._concepts

    def get_round_aliases(self, round_name: str) -> list[AliasEntry]:
        data = self.get_round_snapshot(round_name, "aliases.json")
        if isinstance(data, list):
            return [AliasEntry(**a) for a in data]
        return self._aliases

    def is_okf_stale(self) -> bool:
        """Check whether the OKF bundle has been edited more recently than the
        derived index JSON. When True, run `okf_import.py` to regenerate the
        index from the bundle. Returns False if no OKF bundle exists (then the
        index JSON is treated as authoritative, e.g. in legacy/test setups)."""
        if not OKF_DIR.exists():
            return False
        bundle_mtime = max(p.stat().st_mtime for p in OKF_DIR.rglob("*.md"))
        index_concepts = INDEX_DIR / "concepts.json"
        if not index_concepts.exists():
            return True
        return bundle_mtime > index_concepts.stat().st_mtime


# Module-level singleton
store = DataStore()
