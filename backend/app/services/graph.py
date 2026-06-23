"""
GraphService provides knowledge graph, provenance graph, and failure graph
construction from the knowledge base data.
"""

from app.models.schemas import LinkGraph, GraphNode, GraphEdge, SearchResult
from app.services.data_store import store
from app.services.retrieval import retrieval_service


class GraphService:
    """Builds various graph views from the knowledge base."""

    def get_knowledge_graph(self, round_name: str, issue_type: str | None = None) -> LinkGraph:
        """
        Return the LinkGraph for a given round, optionally filtered by issue type.
        If issue_type is provided, only nodes with matching issue flags are included.
        """
        graph = store.get_round_graph(round_name)

        if issue_type is None:
            return graph

        # Filter nodes by issue_flags
        filtered_nodes = [n for n in graph.nodes if issue_type in n.issue_flags]
        filtered_node_ids = {n.id for n in filtered_nodes}

        # Only include edges where both source and target are in filtered nodes
        filtered_edges = [
            e for e in graph.edges
            if e.source in filtered_node_ids and e.target in filtered_node_ids
        ]

        return LinkGraph(nodes=filtered_nodes, edges=filtered_edges)

    def get_provenance_graph(self, claim_id: str) -> LinkGraph:
        """
        Build a provenance graph for a claim: Source -> Claim -> Page.
        Returns nodes and edges showing the evidence chain.
        """
        claims = store.get_claims()
        claim = next((c for c in claims if c.claim_id == claim_id), None)
        if not claim:
            return LinkGraph()

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        node_ids: set[str] = set()

        # Claim node
        claim_node = GraphNode(
            id=f"claim:{claim.claim_id}",
            type="claim",
            label=f"Claim: {claim.text[:60]}...",
            round_created=claim.round_created,
        )
        nodes.append(claim_node)
        node_ids.add(claim_node.id)

        # Page node
        if claim.page_id:
            page_node = GraphNode(
                id=f"page:{claim.page_id}",
                type="concept_page",
                label=f"Page: {claim.page_id}",
                round_created=claim.round_created,
            )
            if page_node.id not in node_ids:
                nodes.append(page_node)
                node_ids.add(page_node.id)
            edges.append(GraphEdge(
                source=f"claim:{claim.claim_id}",
                target=f"page:{claim.page_id}",
                type="belongs_to",
                round_created=claim.round_created,
            ))

        # Source nodes
        sources = store.get_sources()
        for source_id in claim.source_ids:
            source = next((s for s in sources if s.source_id == source_id), None)
            label = f"Source: {source.title[:50]}..." if source else f"Source: {source_id}"
            src_node = GraphNode(
                id=f"source:{source_id}",
                type="source",
                label=label,
                round_created=source.round if source else claim.round_created,
            )
            if src_node.id not in node_ids:
                nodes.append(src_node)
                node_ids.add(src_node.id)
            edges.append(GraphEdge(
                source=f"source:{source_id}",
                target=f"claim:{claim.claim_id}",
                type="supports",
                round_created=claim.round_created,
            ))

        return LinkGraph(nodes=nodes, edges=edges)

    def get_failure_graph(self, query_id: str) -> LinkGraph:
        """
        Build a graph highlighting expected vs retrieved pages for a query.
        Expected pages that were NOT retrieved are flagged with issue_flags.
        """
        tests = store.get_tests()
        test = next((t for t in tests if t.query_id == query_id), None)
        if not test:
            return LinkGraph()

        graph = store.get_graph()
        round_name = store.get_round_names()[-1] if store.get_round_names() else ""
        retrieved = retrieval_service.search(test.query, round_name, top_k=5)
        retrieved_ids = {r.page_id for r in retrieved}

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        node_ids: set[str] = set()

        # Add query node
        query_node = GraphNode(
            id=f"query:{test.query_id}",
            type="query",
            label=f"Query: {test.query[:60]}...",
            round_created=0,
        )
        nodes.append(query_node)
        node_ids.add(query_node.id)

        # Add expected page nodes
        for page_id in test.expected_pages:
            issue_flags = []
            if page_id not in retrieved_ids:
                issue_flags.append("retrieval_failure")

            # Find node in main graph
            existing = next((n for n in graph.nodes if n.id == page_id), None)
            label = existing.label if existing else page_id

            page_node = GraphNode(
                id=page_id,
                type="concept_page",
                label=label,
                round_created=existing.round_created if existing else 0,
                issue_flags=issue_flags,
            )
            if page_node.id not in node_ids:
                nodes.append(page_node)
                node_ids.add(page_node.id)

            edges.append(GraphEdge(
                source=f"query:{test.query_id}",
                target=page_id,
                type="expected",
                round_created=0,
            ))

            # If retrieved, link to existing graph edges
            if page_id in retrieved_ids:
                for edge in graph.edges:
                    if edge.source == page_id and edge.target not in node_ids:
                        target_node = next((n for n in graph.nodes if n.id == edge.target), None)
                        if target_node:
                            nodes.append(target_node)
                            node_ids.add(target_node.id)
                            edges.append(edge)
                    elif edge.target == page_id and edge.source not in node_ids:
                        source_node = next((n for n in graph.nodes if n.id == edge.source), None)
                        if source_node:
                            nodes.append(source_node)
                            node_ids.add(source_node.id)
                            edges.append(edge)

        # Add retrieved nodes that weren't expected
        for result in retrieved:
            if result.page_id not in test.expected_pages and result.page_id not in node_ids:
                existing = next((n for n in graph.nodes if n.id == result.page_id), None)
                label = existing.label if existing else result.page_id
                retrieved_node = GraphNode(
                    id=result.page_id,
                    type="concept_page",
                    label=label,
                    round_created=existing.round_created if existing else 0,
                    issue_flags=["unexpected_retrieval"],
                )
                nodes.append(retrieved_node)
                node_ids.add(retrieved_node.id)
                edges.append(GraphEdge(
                    source=f"query:{test.query_id}",
                    target=result.page_id,
                    type="retrieved",
                    round_created=0,
                    confidence=result.score,
                ))

        return LinkGraph(nodes=nodes, edges=edges)


# Module-level singleton
graph_service = GraphService()
