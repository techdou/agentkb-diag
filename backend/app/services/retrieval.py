"""
RetrievalService provides search functionality and evaluation of retrieval
performance using TF-IDF-like scoring against concept names, aliases, and claim text.
"""

import math
import re
from collections import Counter

from app.core.tokenize import tokenize as _tokenize
from app.models.schemas import (
    SearchResult,
    RetrievalResult,
    RetrievalTest,
    FailureAttribution,
)
from app.services.data_store import store


def _compute_tf(text: str) -> dict[str, float]:
    """Compute term frequency for a given text."""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    counts = Counter(tokens)
    max_count = max(counts.values())
    return {term: count / max_count for term, count in counts.items()}


def _idf_lookup(all_texts: list[str]) -> dict[str, float]:
    """
    Build an IDF lookup from a corpus of texts.
    idf(t) = 1 + log(N / (1 + df(t)))
    """
    n = len(all_texts)
    df: Counter[str] = Counter()
    for text in all_texts:
        terms = set(_tokenize(text))
        df.update(terms)
    idf: dict[str, float] = {}
    for term, doc_count in df.items():
        idf[term] = 1.0 + math.log(n / (1.0 + doc_count))
    return idf


class RetrievalService:
    """
    Simple TF-IDF-like search over concept names, aliases, and claims.
    Ranks pages by their relevance to the query.
    """

    def _build_page_corpus(self, round_name: str) -> dict[str, str]:
        """
        Build a corpus mapping page_id -> concatenated text
        (canonical name + aliases + associated claim text) for a given round.
        """
        concepts = store.get_round_concepts(round_name)
        claims = store.get_round_claims(round_name)
        aliases = store.get_round_aliases(round_name)

        # Build alias lookup: canonical_name -> list of aliases
        alias_map: dict[str, list[str]] = {}
        for a in aliases:
            if a.canonical not in alias_map:
                alias_map[a.canonical] = []
            alias_map[a.canonical].append(a.alias)

        # Build claims lookup: page_id -> list of claim texts
        claims_by_page: dict[str, list[str]] = {}
        for c in claims:
            if c.page_id not in claims_by_page:
                claims_by_page[c.page_id] = []
            claims_by_page[c.page_id].append(c.text)

        corpus: dict[str, str] = {}
        for concept in concepts:
            page_id = concept.page_id
            parts = [concept.canonical_name]
            # Add concept-level aliases
            if concept.aliases:
                parts.extend(concept.aliases)
            # Add alias entries for this canonical name
            if concept.canonical_name in alias_map:
                parts.extend(alias_map[concept.canonical_name])
            # Add claim text
            if page_id in claims_by_page:
                parts.extend(claims_by_page[page_id])
            corpus[page_id] = " ".join(parts)

        return corpus

    def search(self, query: str, round_name: str, top_k: int = 5) -> list[SearchResult]:
        """
        Search for pages relevant to the query using TF-IDF cosine similarity.
        Returns ranked list of SearchResult items.
        """
        corpus = self._build_page_corpus(round_name)
        if not corpus:
            return []

        all_texts = list(corpus.values())
        idf = _idf_lookup(all_texts)
        query_tf = _compute_tf(query)

        # Build query TF-IDF vector
        query_vec: dict[str, float] = {}
        for term, tf in query_tf.items():
            query_vec[term] = tf * idf.get(term, 1.0)

        query_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0

        # Score each page
        scored: list[tuple[str, float]] = []
        for page_id, text in corpus.items():
            doc_tf = _compute_tf(text)
            doc_vec: dict[str, float] = {}
            for term, tf in doc_tf.items():
                doc_vec[term] = tf * idf.get(term, 1.0)

            dot_product = sum(query_vec.get(term, 0.0) * doc_vec.get(term, 0.0) for term in query_vec)
            doc_norm = math.sqrt(sum(v * v for v in doc_vec.values())) or 1.0
            similarity = dot_product / (query_norm * doc_norm)
            scored.append((page_id, similarity))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Determine if expected pages are hit
        concepts = store.get_round_concepts(round_name)
        concept_pages = {c.page_id for c in concepts}

        results = []
        for page_id, score in scored[:top_k]:
            results.append(SearchResult(
                page_id=page_id,
                score=round(score, 4),
                hit=page_id in concept_pages,
            ))

        return results

    def evaluate(self, round_name: str) -> list[RetrievalResult]:
        """
        Run all retrieval tests and compute results with failure attributions.
        Returns list of RetrievalResult with per-test details.
        """
        tests = store.get_tests()
        results: list[RetrievalResult] = []

        for test in tests:
            retrieved = self.search(test.query, round_name, top_k=5)
            retrieved_ids = [r.page_id for r in retrieved]
            expected_set = set(test.expected_pages)
            all_hit = all(pid in retrieved_ids for pid in test.expected_pages)

            result = RetrievalResult(
                query_id=test.query_id,
                query=test.query,
                expected_pages=test.expected_pages,
                retrieved_pages=retrieved,
                all_hit=all_hit,
            )

            if not all_hit:
                graph = store.get_round_graph(round_name)
                concepts = store.get_round_concepts(round_name)
                aliases = store.get_round_aliases(round_name)
                missed = [pid for pid in test.expected_pages if pid not in retrieved_ids]
                failures = self._attribute_failures(test, retrieved, graph, concepts, aliases, missed)
                for f in failures:
                    result.failure_reasons.append(f.reason)
                    result.suggestions.append(f.suggestion)

            results.append(result)

        return results

    def _attribute_failures(
        self,
        test: RetrievalTest,
        retrieved_pages: list[SearchResult],
        graph: "LinkGraph",
        concepts: list["Concept"],
        aliases: list["AliasEntry"],
        missed_pages: list[str],
    ) -> list[FailureAttribution]:
        """
        Determine WHY expected pages weren't retrieved.
        Checks: orphan pages, missing aliases, broken links, name mismatches.
        """
        attributions: list[FailureAttribution] = []

        concept_map = {c.page_id: c for c in concepts}
        node_ids = {n.id for n in graph.nodes}
        connected_ids = set()
        for edge in graph.edges:
            connected_ids.add(edge.source)
            connected_ids.add(edge.target)

        for pid in missed_pages:
            concept = concept_map.get(pid)
            if not concept:
                attributions.append(FailureAttribution(
                    reason="page_not_found",
                    detail=f"Expected page '{pid}' does not exist in concepts index.",
                    suggestion="Ensure the page is properly indexed.",
                ))
                continue

            # Check orphan
            if pid not in connected_ids:
                attributions.append(FailureAttribution(
                    reason="orphan_page",
                    detail=f"Page '{concept.canonical_name}' ({pid}) is an orphan with no links.",
                    suggestion="Add wikilinks to this page to improve discoverability.",
                ))

            # Check name mismatch: does the canonical name appear in the query?
            query_lower = test.query.lower()
            name_parts = concept.canonical_name.lower().split()
            if not any(part in query_lower for part in name_parts):
                attributions.append(FailureAttribution(
                    reason="name_mismatch",
                    detail=f"Query '{test.query}' does not match concept name '{concept.canonical_name}'.",
                    suggestion="Consider adding synonyms or aliases for '{concept.canonical_name}'.",
                ))

            # Check missing aliases
            concept_aliases = [a for a in aliases if a.canonical == concept.canonical_name]
            query_terms = set(_tokenize(test.query))
            alias_terms = set()
            for a in concept_aliases:
                alias_terms.update(_tokenize(a.alias))
            if not (query_terms & alias_terms):
                attributions.append(FailureAttribution(
                    reason="alias_missing",
                    detail=f"No alias matches query terms for concept '{concept.canonical_name}'.",
                    suggestion=f"Add query-related aliases to concept '{concept.canonical_name}'.",
                ))

        return attributions

    def attribute_failure(
        self,
        test: RetrievalTest,
        retrieved_pages: list[SearchResult],
        graph: "LinkGraph",
        concepts: list["Concept"],
        aliases: list["AliasEntry"],
    ) -> list[FailureAttribution]:
        """Convenience wrapper that calls _attribute_failures with computed missed pages."""
        retrieved_ids = {r.page_id for r in retrieved_pages}
        missed = [pid for pid in test.expected_pages if pid not in retrieved_ids]
        return self._attribute_failures(test, retrieved_pages, graph, concepts, aliases, missed)


# Module-level singleton
retrieval_service = RetrievalService()
