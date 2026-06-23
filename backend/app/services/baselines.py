"""
Baseline Retrievers for experiment comparison.

Implements 4 retrieval methods to compare against AgentKB-Diag:
  1. RawDocRAG      — Index raw source documents directly (no wiki structure)
  2. StaticWikiRAG  — Index Round 1 wiki pages only (frozen)
  3. AgentWikiRAG   — Index the Agent-maintained wiki (current round)
  4. AgentKBDiag    — Agent-maintained wiki + diagnosis-driven repair
"""

import math
import re
import os
import json
from collections import Counter
from pathlib import Path
from typing import Optional

from app.core.tokenize import tokenize as _tokenize
from app.models.schemas import SearchResult, Concept, Claim, LinkGraph, AliasEntry
from app.services.data_store import store


# Compute paths relative to the project root
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
PROJECT_ROOT = BACKEND_DIR.parent  # agentkb-diag/
CONVERTED_DIR = PROJECT_ROOT / "data" / "converted"
REPORTS_DIR = PROJECT_ROOT / "workspace" / "reports"


def _compute_tf(text: str) -> dict[str, float]:
    """Compute term frequency for a given text."""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    counts = Counter(tokens)
    max_count = max(counts.values())
    return {term: count / max_count for term, count in counts.items()}


def _build_idf(all_texts: list[str]) -> dict[str, float]:
    """Build IDF lookup from a corpus of texts."""
    n = len(all_texts)
    df: Counter[str] = Counter()
    for text in all_texts:
        terms = set(_tokenize(text))
        df.update(terms)
    idf: dict[str, float] = {}
    for term, doc_count in df.items():
        idf[term] = 1.0 + math.log(n / (1.0 + doc_count))
    return idf


def _cosine_similarity(
    query_vec: dict[str, float],
    doc_vec: dict[str, float],
) -> float:
    """Compute cosine similarity between two sparse vectors."""
    dot = sum(query_vec.get(t, 0.0) * doc_vec.get(t, 0.0) for t in query_vec)
    q_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0
    d_norm = math.sqrt(sum(v * v for v in doc_vec.values())) or 1.0
    return dot / (q_norm * d_norm)


class BaselineRetriever:
    """Abstract baseline for retrieval comparison."""

    def __init__(self, data_paths: Optional[dict] = None):
        self._data_paths = data_paths or {}
        self._corpus: dict[str, str] = {}
        self._idf: dict[str, float] = {}
        self._page_ids: list[str] = []

    @property
    def name(self) -> str:
        raise NotImplementedError

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Search and return ranked results."""
        if not self._corpus:
            return []

        all_texts = list(self._corpus.values())
        local_idf = _build_idf(all_texts)
        query_tf = _compute_tf(query)
        query_vec = {
            t: tf * local_idf.get(t, 1.0)
            for t, tf in query_tf.items()
        }

        scored: list[tuple[str, float]] = []
        for page_id, text in self._corpus.items():
            doc_tf = _compute_tf(text)
            doc_vec = {
                t: tf * local_idf.get(t, 1.0)
                for t, tf in doc_tf.items()
            }
            sim = _cosine_similarity(query_vec, doc_vec)
            scored.append((page_id, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            SearchResult(page_id=pid, score=round(s, 4), hit=True)
            for pid, s in scored[:top_k]
        ]


class RawDocRAG(BaselineRetriever):
    """
    Index raw source documents directly from data/converted/.
    No wiki structure — each source file is a separate document.
    """

    def __init__(self, data_paths: Optional[dict] = None):
        super().__init__(data_paths)
        self._load_raw_docs()

    @property
    def name(self) -> str:
        return "raw_doc_rag"

    def _load_raw_docs(self) -> None:
        """Load all converted source documents as separate pages."""
        corpus: dict[str, str] = {}
        converted_dir = self._data_paths.get("converted_dir", CONVERTED_DIR)

        if not converted_dir.exists():
            return

        for round_dir in sorted(converted_dir.iterdir()):
            if not round_dir.is_dir():
                continue
            # Index both .md and .txt converted documents. The legacy code
            # globbed only *.txt while the actual corpus is *.md, which silently
            # fell back to a synthetic claims-only corpus and invalidated the
            # raw_doc_rag baseline.
            doc_files = sorted(
                [*round_dir.glob("*.md"), *round_dir.glob("*.txt")]
            )
            for doc_file in doc_files:
                try:
                    with open(doc_file, "r", encoding="utf-8") as f:
                        content = f.read()
                except (OSError, UnicodeDecodeError):
                    content = ""
                if content.strip():
                    # doc_id = source_id (e.g. "source_001"), so the evaluator can
                    # map a retrieved source back to the concepts it supports via
                    # the claim source_ids. The stem is "source_XXX_converted" —
                    # strip the "_converted" suffix to recover the canonical id.
                    stem = doc_file.stem
                    source_id = stem.replace("_converted", "")
                    corpus[source_id] = content

        # If no raw docs found, create synthetic corpus from claims
        if not corpus:
            corpus = self._build_from_claims()

        self._corpus = corpus
        self._page_ids = list(corpus.keys())

    def _build_from_claims(self) -> dict[str, str]:
        """Fallback: build corpus from all claims across all rounds as synthetic docs."""
        corpus: dict[str, str] = {}
        claims = store.get_claims()
        sources = store.get_sources()
        source_map = {s.source_id: s for s in sources}

        for claim in claims:
            source_id = claim.source_ids[0] if claim.source_ids else "unknown"
            doc_id = f"raw_doc_{source_id}"
            if doc_id not in corpus:
                source = source_map.get(source_id)
                src_text = f"{source.title} ({source.year})" if source else f"Source {source_id}"
                corpus[doc_id] = src_text
            corpus[doc_id] += " " + claim.text

        return corpus


class StaticWikiRAG(BaselineRetriever):
    """
    Index Round 1 wiki pages only — frozen snapshot, no updates across rounds.
    Represents a "build once and never maintain" strategy.
    """

    def __init__(self, data_paths: Optional[dict] = None):
        super().__init__(data_paths)
        self._load_round1_wiki()

    @property
    def name(self) -> str:
        return "static_wiki"

    def _load_round1_wiki(self) -> None:
        """Build corpus from round_1 snapshot of concepts, claims, and aliases."""
        corpus: dict[str, str] = {}

        concepts = store.get_round_concepts("round_1")
        claims = store.get_round_claims("round_1")
        aliases = store.get_round_aliases("round_1")

        # Build alias lookup
        alias_map: dict[str, list[str]] = {}
        for a in aliases:
            if a.canonical not in alias_map:
                alias_map[a.canonical] = []
            alias_map[a.canonical].append(a.alias)

        # Build claims lookup by page
        claims_by_page: dict[str, list[str]] = {}
        for c in claims:
            if c.page_id not in claims_by_page:
                claims_by_page[c.page_id] = []
            claims_by_page[c.page_id].append(c.text)

        for concept in concepts:
            page_id = concept.page_id
            parts = [concept.canonical_name]
            if concept.aliases:
                parts.extend(concept.aliases)
            if concept.canonical_name in alias_map:
                parts.extend(alias_map[concept.canonical_name])
            if page_id in claims_by_page:
                parts.extend(claims_by_page[page_id])
            corpus[page_id] = " ".join(parts)

        self._corpus = corpus
        self._page_ids = list(corpus.keys())


class AgentWikiRAG(BaselineRetriever):
    """
    Index the Agent-maintained wiki at the current round.
    Wraps the same indexing logic as RetrievalService but exposed as a baseline.
    """

    def __init__(self, data_paths: Optional[dict] = None):
        super().__init__(data_paths)
        self._round_name = data_paths.get("round_name", "round_3") if data_paths else "round_3"
        self._load_round_wiki(self._round_name)

    @property
    def name(self) -> str:
        return "agent_wiki"

    def set_round(self, round_name: str) -> None:
        """Switch the round to index."""
        self._round_name = round_name
        self._load_round_wiki(round_name)

    def _load_round_wiki(self, round_name: str) -> None:
        """Build corpus from the specified round's snapshot."""
        corpus: dict[str, str] = {}

        concepts = store.get_round_concepts(round_name)
        claims = store.get_round_claims(round_name)
        aliases = store.get_round_aliases(round_name)

        alias_map: dict[str, list[str]] = {}
        for a in aliases:
            if a.canonical not in alias_map:
                alias_map[a.canonical] = []
            alias_map[a.canonical].append(a.alias)

        claims_by_page: dict[str, list[str]] = {}
        for c in claims:
            if c.page_id not in claims_by_page:
                claims_by_page[c.page_id] = []
            claims_by_page[c.page_id].append(c.text)

        for concept in concepts:
            page_id = concept.page_id
            parts = [concept.canonical_name]
            if concept.aliases:
                parts.extend(concept.aliases)
            if concept.canonical_name in alias_map:
                parts.extend(alias_map[concept.canonical_name])
            if page_id in claims_by_page:
                parts.extend(claims_by_page[page_id])
            corpus[page_id] = " ".join(parts)

        self._corpus = corpus
        self._page_ids = list(corpus.keys())


class AgentKBDiag(BaselineRetriever):
    """
    Agent-maintained wiki + diagnosis-driven repair, forming a closed loop:
      diagnose (find_issues) → detect (statistical anomaly) → repair → reindex.

    The repair is performed by RepairEngine (app.services.repair), which consumes
    the structured Issue list from diagnosis AND applies dual-signal statistical
    anomaly detection to clean polluted claim text. No hardcoded concept pairs,
    alias tables, or noise-word lists — the algorithm infers anomalies purely
    from token statistics. See repair.py for the academic-integrity rationale.

    The repair happens in memory: the on-disk round snapshots are never mutated.
    The repaired corpus is what this retriever indexes.
    """

    def __init__(self, data_paths: Optional[dict] = None):
        super().__init__(data_paths)
        self._round_name = data_paths.get("round_name", "round_3") if data_paths else "round_3"
        self._load_repaired_wiki()

    @property
    def name(self) -> str:
        return "agentkb_diag"

    def _load_repaired_wiki(self) -> None:
        """Run diagnosis-driven repair on the round's data, then build the
        repaired corpus using the same indexing logic as AgentWikiRAG."""
        # Import here to avoid a circular import at module load time
        # (repair.py imports from data_store / diagnosis; baselines is imported
        # widely, so deferring keeps the dependency graph clean).
        from app.services.repair import repair_engine

        repaired = repair_engine.repair(self._round_name)

        # Build corpus from repaired data — identical construction to
        # AgentWikiRAG._load_round_wiki so the only difference between
        # agent_wiki and agentkb_diag is the applied repair.
        concepts = repaired.concepts
        claims = repaired.claims
        aliases = repaired.aliases

        alias_map: dict[str, list[str]] = {}
        for a in aliases:
            alias_map.setdefault(a.canonical, []).append(a.alias)

        claims_by_page: dict[str, list[str]] = {}
        for c in claims:
            claims_by_page.setdefault(c.page_id, []).append(c.text)

        corpus: dict[str, str] = {}
        for concept in concepts:
            page_id = concept.page_id
            parts = [concept.canonical_name]
            if concept.aliases:
                parts.extend(concept.aliases)
            if concept.canonical_name in alias_map:
                parts.extend(alias_map[concept.canonical_name])
            if page_id in claims_by_page:
                parts.extend(claims_by_page[page_id])
            corpus[page_id] = " ".join(parts)

        self._corpus = corpus
        self._page_ids = list(corpus.keys())
        # Expose repair audit info for debugging / experiment logging
        self._repair_actions = repaired.actions


def compute_baseline_metrics(
    retriever: BaselineRetriever,
    test_queries: list[dict],
    expected_map: dict[str, set[str]],
    top_k: int = 3,
    id_mapper: Optional[dict[str, set[str]]] = None,
) -> dict:
    """
    Run a baseline retriever against all test queries and compute Recall@k and MRR.

    Args:
        retriever: A BaselineRetriever instance
        test_queries: List of query dicts with 'query_id' and 'query' keys
        expected_map: Mapping from query_id -> set of expected page_ids
        top_k: k for Recall@k
        id_mapper: Optional mapping from a retrieved id (e.g. a source_id for
            RawDocRAG) to the set of concept page_ids it supports. When a
            retrieved id is not directly in `expected`, its mapped concept ids
            are checked instead. This lets a source-document retriever be scored
            against concept-level expectations.

    Returns:
        dict with recall_at_k, mrr, total_queries, passed_queries, per_query
    """
    total = len(test_queries)
    if total == 0:
        return {
            "recall_at_k": 0.0,
            "mrr": 0.0,
            "total_queries": 0,
            "passed_queries": 0,
            "per_query": [],
        }

    def _matched_ids(pid: str) -> set[str]:
        """Resolve a retrieved id to the set of concept ids it counts as."""
        ids = {pid}
        if id_mapper and pid in id_mapper:
            ids |= id_mapper[pid]
        return ids

    hits = 0
    reciprocal_sum = 0.0
    per_query: list[dict] = []

    for tq in test_queries:
        qid = tq["query_id"]
        query = tq["query"]
        expected = expected_map.get(qid, set())

        results = retriever.search(query, top_k=max(top_k, 50))

        # Recall@k: at least one expected page in top-k (allowing id mapping).
        top_results = results[:top_k]
        hit = any(expected & _matched_ids(r.page_id) for r in top_results)
        if hit:
            hits += 1

        # MRR: rank of first relevant result (search across all results).
        rank = None
        for i, r in enumerate(results):
            if expected & _matched_ids(r.page_id):
                rank = i + 1
                break
        if rank is not None:
            reciprocal_sum += 1.0 / rank

        per_query.append({
            "query_id": qid,
            "query": query,
            "hit": hit,
            "retrieved_ids": [r.page_id for r in top_results],
        })

    return {
        "recall_at_k": hits / total,
        "mrr": reciprocal_sum / total,
        "total_queries": total,
        "passed_queries": hits,
        "per_query": per_query,
    }
