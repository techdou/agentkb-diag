"""
DiagnosisService provides health metrics and issue detection
for wiki knowledge bases across different rounds.
"""

from app.models.schemas import HealthReport, Issue, Claim, LinkGraph, AliasEntry, Concept
from app.services.data_store import store


class DiagnosisService:
    """Computes health metrics and finds issues in the knowledge base."""

    def compute_citation_coverage(self, claims: list[Claim]) -> float:
        """Fraction of claims that have at least one source citation."""
        if not claims:
            return 0.0
        cited = sum(1 for c in claims if c.source_ids)
        return cited / len(claims)

    def compute_unsupported_claim_rate(self, claims: list[Claim]) -> float:
        """Fraction of claims with status 'unsupported'."""
        if not claims:
            return 0.0
        unsupported = sum(1 for c in claims if c.status == "unsupported")
        return unsupported / len(claims)

    def compute_orphan_rate(self, graph: LinkGraph) -> float:
        """Fraction of nodes that have no edges (orphans)."""
        if not graph.nodes:
            return 0.0
        node_ids = {n.id for n in graph.nodes}
        connected_ids = set()
        for edge in graph.edges:
            connected_ids.add(edge.source)
            connected_ids.add(edge.target)
        orphan_count = len(node_ids - connected_ids)
        return orphan_count / len(graph.nodes)

    def compute_duplicate_rate(self, aliases: list[AliasEntry], concepts: list[Concept]) -> float:
        """
        Fraction of concepts that have at least one suggested alias (potential duplicate).
        Uses suggested-alias entries as a proxy for duplicate detection.
        """
        if not concepts:
            return 0.0
        # Count concepts that have suggested aliases pointing to them
        concept_ids = {c.concept_id for c in concepts}
        canonical_names = {a.canonical for a in aliases if a.status == "suggested"}
        # Match aliases against concept canonical names
        concept_canonicals = {c.canonical_name for c in concepts}
        duplicates = canonical_names & concept_canonicals
        # Also check aliases that are listed in concepts
        alias_names = set()
        for a in aliases:
            if a.status == "suggested":
                alias_names.add(a.alias)
        suggested_count = sum(1 for c in concepts if c.canonical_name in canonical_names or c.canonical_name in alias_names)
        return suggested_count / len(concepts)

    def compute_conflict_density(self, claims: list[Claim]) -> float:
        """Fraction of claims with status 'conflicted'."""
        if not claims:
            return 0.0
        conflicted = sum(1 for c in claims if c.status == "conflicted")
        return conflicted / len(claims)

    def compute_recall_at_3(self, round_name: str) -> float:
        """
        Approximate Recall@3 using the retrieval tests.
        For each test, check if any expected page is in top-3 retrieved results.
        """
        from app.services.retrieval import RetrievalService
        rs = RetrievalService()
        tests = store.get_tests()
        if not tests:
            return 0.0
        hits = 0
        for test in tests:
            results = rs.search(test.query, round_name, top_k=3)
            expected = set(test.expected_pages)
            hit = any(r.page_id in expected for r in results)
            if hit:
                hits += 1
        return hits / len(tests)

    def compute_mrr(self, round_name: str) -> float:
        """Mean Reciprocal Rank: average of 1/rank for first relevant result."""
        from app.services.retrieval import RetrievalService
        rs = RetrievalService()
        tests = store.get_tests()
        if not tests:
            return 0.0
        total_reciprocal = 0.0
        for test in tests:
            results = rs.search(test.query, round_name, top_k=50)
            expected = set(test.expected_pages)
            rank = None
            for i, r in enumerate(results):
                if r.page_id in expected:
                    rank = i + 1
                    break
            if rank is not None:
                total_reciprocal += 1.0 / rank
        return total_reciprocal / len(tests)

    def compute_all_metrics(self, round_name: str) -> HealthReport:
        """Compute all health metrics for a given round and return a HealthReport.
        Loads pre-computed values from the round's health_report.json if available."""
        precomputed = store.get_round_snapshot(round_name, "health_report.json")
        if isinstance(precomputed, dict) and precomputed.get("citation_coverage") is not None:
            # Map from stored format to HealthReport fields
            details = precomputed.get("metrics_detail", {})
            # Try loading retrieval eval for recall@3 and MRR
            eval_data = store.get_round_snapshot(round_name, "retrieval_eval.json")
            recall3 = precomputed.get("recall_at_3") or 0.0
            mrr_val = precomputed.get("mrr") or 0.0
            if isinstance(eval_data, dict):
                recall3 = recall3 or eval_data.get("recall_at_3") or 0.0
                mrr_val = mrr_val or eval_data.get("mrr") or 0.0

            return HealthReport(
                round_name=round_name,
                citation_coverage=precomputed.get("citation_coverage", 0.0),
                unsupported_claim_rate=precomputed.get("unsupported_claim_rate", 0.0),
                orphan_rate=precomputed.get("orphan_rate", 0.0),
                duplicate_rate=precomputed.get("duplicate_rate", 0.0),
                conflict_density=precomputed.get("conflict_density", 0.0),
                recall_at_3=round(recall3, 4),
                mrr=round(mrr_val, 4),
                page_count=precomputed.get("page_count", details.get("total_pages", 0)),
                claim_count=precomputed.get("claim_count", details.get("total_claims", 0)),
                source_count=precomputed.get("source_count", 0),
                issue_count=precomputed.get("issue_count",
                    details.get("orphan_pages", 0) + details.get("duplicate_pairs", 0) + details.get("conflict_pairs", 0) + details.get("unsupported_claims", 0)),
            )

        claims = store.get_round_claims(round_name)
        sources = store.get_round_sources(round_name)
        graph = store.get_round_graph(round_name)
        concepts = store.get_round_concepts(round_name)
        aliases = store.get_round_aliases(round_name)
        issues = self.find_issues(round_name)

        citation_cov = self.compute_citation_coverage(claims)
        unsupported_rate = self.compute_unsupported_claim_rate(claims)
        orphan_rate = self.compute_orphan_rate(graph)
        duplicate_rate = self.compute_duplicate_rate(aliases, concepts)
        conflict_density = self.compute_conflict_density(claims)
        recall_at_3 = self.compute_recall_at_3(round_name)
        mrr = self.compute_mrr(round_name)

        return HealthReport(
            round_name=round_name,
            citation_coverage=round(citation_cov, 4),
            unsupported_claim_rate=round(unsupported_rate, 4),
            orphan_rate=round(orphan_rate, 4),
            duplicate_rate=round(duplicate_rate, 4),
            conflict_density=round(conflict_density, 4),
            recall_at_3=round(recall_at_3, 4),
            mrr=round(mrr, 4),
            page_count=len(graph.nodes),
            claim_count=len(claims),
            source_count=len(sources),
            issue_count=len(issues),
        )

    def find_issues(self, round_name: str) -> list[Issue]:
        """
        Scan the knowledge base for issues and return a list of Issues.
        Detects: orphan pages, potential duplicates, conflicted claims,
        missing citations, and broken links.
        """
        issues: list[Issue] = []
        claims = store.get_round_claims(round_name)
        graph = store.get_round_graph(round_name)
        concepts = store.get_round_concepts(round_name)
        aliases = store.get_round_aliases(round_name)

        issue_id_counter = [0]

        def next_issue_id(prefix: str) -> str:
            issue_id_counter[0] += 1
            return f"{prefix}_{issue_id_counter[0]:04d}"

        # --- Orphan detection ---
        node_ids = {n.id for n in graph.nodes}
        connected_ids = set()
        for edge in graph.edges:
            connected_ids.add(edge.source)
            connected_ids.add(edge.target)
        orphans = node_ids - connected_ids
        # Filter to pages that actually exist in concepts (meaningful orphans)
        concept_pages = {c.page_id for c in concepts}
        relevant_orphans = orphans & concept_pages if concept_pages else orphans
        for node_id in list(relevant_orphans)[:20]:  # limit to 20
            node = next((n for n in graph.nodes if n.id == node_id), None)
            label = node.label if node else node_id
            issues.append(Issue(
                issue_id=next_issue_id("orphan"),
                type="orphan",
                severity="medium",
                page_id=node_id,
                description=f"Page '{label}' has no incoming or outgoing links.",
                suggestion="Consider adding wikilinks to integrate this page into the knowledge graph.",
            ))

        # --- Duplicate detection via aliases ---
        canonical_names = {c.canonical_name for c in concepts}
        for alias in aliases:
            if alias.status == "suggested" and alias.canonical in canonical_names:
                issues.append(Issue(
                    issue_id=next_issue_id("duplicate"),
                    type="duplicate",
                    severity="medium",
                    page_id="",
                    description=f"Potential duplicate: alias '{alias.alias}' suggests concept '{alias.canonical}' may have duplicate pages.",
                    suggestion=f"Review and merge pages related to '{alias.alias}' and '{alias.canonical}'.",
                ))

        # --- Conflict detection ---
        for claim in claims:
            if claim.status == "conflicted":
                issues.append(Issue(
                    issue_id=next_issue_id("conflict"),
                    type="conflict",
                    severity="high",
                    page_id=claim.page_id,
                    description=f"Claim '{claim.claim_id}' has conflicting evidence: '{claim.text[:100]}...'",
                    suggestion="Review sources and reconcile conflicting information.",
                ))

        # --- Missing citation detection ---
        for claim in claims:
            if claim.status == "unsupported" or not claim.source_ids:
                issues.append(Issue(
                    issue_id=next_issue_id("missing_citation"),
                    type="missing_citation",
                    severity="high",
                    page_id=claim.page_id,
                    description=f"Claim '{claim.claim_id}' lacks supporting citations: '{claim.text[:100]}...'",
                    suggestion="Add source citations to support this claim.",
                ))

        # --- Broken link detection ---
        all_node_ids = node_ids
        for edge in graph.edges:
            if edge.source not in all_node_ids:
                issues.append(Issue(
                    issue_id=next_issue_id("broken_link"),
                    type="broken_link",
                    severity="low",
                    page_id=edge.source,
                    description=f"Broken link: edge source '{edge.source}' does not exist in nodes.",
                    suggestion="Remove or fix the broken edge reference.",
                ))
            if edge.target not in all_node_ids:
                issues.append(Issue(
                    issue_id=next_issue_id("broken_link"),
                    type="broken_link",
                    severity="low",
                    page_id=edge.target,
                    description=f"Broken link: edge target '{edge.target}' does not exist in nodes.",
                    suggestion="Remove or fix the broken edge reference.",
                ))

        return issues

    def get_fix_suggestions(self, issue_type: str) -> list[str]:
        """Return predefined fix suggestions for a given issue type."""
        suggestions = {
            "orphan": [
                "Add incoming wikilinks from related pages.",
                "Create a hub page that links to orphan pages.",
                "Review if the orphan page should be merged into another page.",
            ],
            "duplicate": [
                "Merge duplicate pages into a single canonical page.",
                "Set up proper alias redirects.",
                "Consolidate claims from duplicate pages.",
            ],
            "conflict": [
                "Review conflicting sources and determine which is correct.",
                "Add a note explaining the disagreement.",
                "Update claim status after resolution.",
            ],
            "broken_link": [
                "Update the edge to point to an existing node.",
                "Remove the broken edge from the graph.",
                "Create the missing target page if it was intended.",
            ],
            "missing_citation": [
                "Find and add supporting sources.",
                "Mark the claim as unsupported if no source exists.",
                "Remove unsupported claims.",
            ],
        }
        return suggestions.get(issue_type, ["No specific suggestions available."])


# Module-level singleton
diagnosis_service = DiagnosisService()
