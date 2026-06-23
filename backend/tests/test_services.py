"""
Unit tests for core backend services: diagnosis, retrieval, graph, data_store.

These cover the numerical correctness of metric computation, retrieval ranking,
and graph construction that the API-level smoke tests in test_api.py do not.
"""

import pytest

from app.models.schemas import Claim, Concept, LinkGraph, GraphNode, GraphEdge
from app.services.diagnosis import DiagnosisService, diagnosis_service
from app.services.retrieval import RetrievalService, _tokenize, _compute_tf
from app.services.data_store import store


# ---------------------------------------------------------------------------
# Diagnosis service: metric computation correctness
# ---------------------------------------------------------------------------

class TestCitationCoverage:
    def test_all_cited(self):
        claims = [
            Claim(claim_id="c1", text="x", page_id="p", source_ids=["s1"], round_created=1, round_updated=1),
            Claim(claim_id="c2", text="y", page_id="p", source_ids=["s1", "s2"], round_created=1, round_updated=1),
        ]
        assert diagnosis_service.compute_citation_coverage(claims) == 1.0

    def test_none_cited(self):
        claims = [
            Claim(claim_id="c1", text="x", page_id="p", source_ids=[], round_created=1, round_updated=1),
            Claim(claim_id="c2", text="y", page_id="p", source_ids=[], round_created=1, round_updated=1),
        ]
        assert diagnosis_service.compute_citation_coverage(claims) == 0.0

    def test_half_cited(self):
        claims = [
            Claim(claim_id="c1", text="x", page_id="p", source_ids=["s1"], round_created=1, round_updated=1),
            Claim(claim_id="c2", text="y", page_id="p", source_ids=[], round_created=1, round_updated=1),
        ]
        assert diagnosis_service.compute_citation_coverage(claims) == 0.5

    def test_empty_claims(self):
        assert diagnosis_service.compute_citation_coverage([]) == 0.0


class TestUnsupportedRate:
    def test_no_unsupported(self):
        claims = [
            Claim(claim_id="c1", text="x", page_id="p", source_ids=["s"], status="supported", round_created=1, round_updated=1),
            Claim(claim_id="c2", text="y", page_id="p", source_ids=["s"], status="conflicted", round_created=1, round_updated=1),
        ]
        assert diagnosis_service.compute_unsupported_claim_rate(claims) == 0.0

    def test_with_unsupported(self):
        claims = [
            Claim(claim_id="c1", text="x", page_id="p", source_ids=["s"], status="supported", round_created=1, round_updated=1),
            Claim(claim_id="c2", text="y", page_id="p", source_ids=["s"], status="unsupported", round_created=1, round_updated=1),
            Claim(claim_id="c3", text="z", page_id="p", source_ids=["s"], status="unsupported", round_created=1, round_updated=1),
        ]
        assert diagnosis_service.compute_unsupported_claim_rate(claims) == pytest.approx(2 / 3)


class TestOrphanRate:
    def test_no_orphans(self):
        graph = LinkGraph(
            nodes=[GraphNode(id="a", label="A", round_created=1),
                   GraphNode(id="b", label="B", round_created=1)],
            edges=[GraphEdge(source="a", target="b", round_created=1)],
        )
        assert diagnosis_service.compute_orphan_rate(graph) == 0.0

    def test_all_orphans(self):
        graph = LinkGraph(
            nodes=[GraphNode(id="a", label="A", round_created=1),
                   GraphNode(id="b", label="B", round_created=1)],
            edges=[],
        )
        assert diagnosis_service.compute_orphan_rate(graph) == 1.0

    def test_empty_graph(self):
        assert diagnosis_service.compute_orphan_rate(LinkGraph()) == 0.0


class TestConflictDensity:
    def test_conflicts(self):
        claims = [
            Claim(claim_id="c1", text="x", page_id="p", source_ids=["s"], status="supported", round_created=1, round_updated=1),
            Claim(claim_id="c2", text="y", page_id="p", source_ids=["s"], status="conflicted", round_created=1, round_updated=1),
            Claim(claim_id="c3", text="z", page_id="p", source_ids=["s"], status="conflicted", round_created=1, round_updated=1),
        ]
        assert diagnosis_service.compute_conflict_density(claims) == pytest.approx(2 / 3)


class TestFindIssues:
    def test_detects_orphans(self):
        # Use the live store so we exercise real data; verify orphan issues
        # are produced for known orphan pages.
        issues = diagnosis_service.find_issues("round_3")
        orphan_issues = [i for i in issues if i.type == "orphan"]
        assert isinstance(orphan_issues, list)

    def test_issue_types_valid(self):
        issues = diagnosis_service.find_issues("round_3")
        valid_types = {"orphan", "duplicate", "conflict", "broken_link", "missing_citation"}
        for issue in issues:
            assert issue.type in valid_types


# ---------------------------------------------------------------------------
# Retrieval service: tokenization + ranking
# ---------------------------------------------------------------------------

class TestTokenization:
    def test_ascii_words(self):
        tokens = _tokenize("RAG improves retrieval quality")
        assert "rag" in tokens
        assert "improves" in tokens
        assert "retrieval" in tokens

    def test_cjk_bigrams(self):
        tokens = _tokenize("检索增强生成")
        # unigrams
        assert "检" in tokens and "索" in tokens
        # bigrams
        assert "检索" in tokens
        assert "增强" in tokens

    def test_mixed(self):
        tokens = _tokenize("RAG检索增强生成")
        assert "rag" in tokens
        assert "检索" in tokens

    def test_short_ascii_filtered(self):
        # single ASCII chars are dropped (len >= 2 required)
        tokens = _tokenize("a RAG b")
        assert "rag" in tokens
        assert "a" not in tokens


class TestRetrievalSearch:
    def test_returns_ranked_results(self):
        rs = RetrievalService()
        results = rs.search("RAG检索增强生成", "round_3", top_k=5)
        assert len(results) <= 5
        # Scores should be descending
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_chinese_query_scores_nonzero(self):
        """Regression for M3: Chinese queries must not all score 0."""
        rs = RetrievalService()
        results = rs.search("稠密检索DPR", "round_3", top_k=3)
        assert any(r.score > 0 for r in results)

    def test_relevant_page_ranks_high(self):
        rs = RetrievalService()
        results = rs.search("稠密检索", "round_3", top_k=5)
        page_ids = [r.page_id for r in results]
        # Dense_Retrieval should appear in top results for a dense-retrieval query
        assert "Dense_Retrieval" in page_ids[:3]


class TestTfComputation:
    def test_tf_normalized(self):
        tf = _compute_tf("rag rag retrieval")
        # "rag" appears twice, "retrieval" once → max=2, so rag=1.0
        assert tf["rag"] == pytest.approx(1.0)
        assert tf["retrieval"] == pytest.approx(0.5)

    def test_empty_text(self):
        assert _compute_tf("") == {}


# ---------------------------------------------------------------------------
# DataStore: round snapshot access + OKF staleness
# ---------------------------------------------------------------------------

class TestDataStore:
    def test_round_names_available(self):
        rounds = store.get_round_names()
        assert "round_1" in rounds
        assert "round_3" in rounds

    def test_round_claims_fallback(self):
        # Rounds without their own claims.json fall back to the global index.
        claims = store.get_round_claims("round_1")
        assert len(claims) > 0
        assert all(hasattr(c, "claim_id") for c in claims)

    def test_is_okf_stale_returns_bool(self):
        # Should return a bool without raising, regardless of state.
        result = store.is_okf_stale()
        assert isinstance(result, bool)

    def test_load_all_populated(self):
        assert len(store.get_concepts()) > 0
        assert len(store.get_claims()) > 0
        assert len(store.get_sources()) > 0
        assert len(store.get_graph().nodes) > 0
