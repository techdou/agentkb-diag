"""Curated manifest of 30 real RAG papers, one per source slot.

Each entry pins a specific arXiv id to a source_NNN slot and records the
mapping rationale (whether the paper is the exact one previewed by the
original data/raw stub, or a real same-topic replacement for a fabricated
stub). This makes the dataset reproducible and traceable.

Used by fetch_papers_by_id.py to download PDFs deterministically.
"""

from __future__ import annotations

# Mapping category codes (recorded in frontmatter for traceability):
#   "exact"   — the original source_NNN.md stub already named this real paper
#   "approx"  — real paper, angle slightly differs from the stub description
#   "replace" — original stub was fabricated; this is a real same-topic paper

PAPER_MANIFEST: list[dict] = [
    # ---------------------------------------------------------------- Round 1
    {
        "source_id": "source_001", "round": 1, "arxiv_id": "2004.04906",
        "title": "Dense Passage Retrieval for Open-Domain Question Answering",
        "mapping": "exact",
    },
    {
        "source_id": "source_002", "round": 1, "arxiv_id": "2005.11401",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "mapping": "exact",
    },
    {
        "source_id": "source_003", "round": 1, "arxiv_id": "2112.09118",
        "title": "Unsupervised Dense Information Retrieval with Contrastive Learning",
        "mapping": "replace",
        "note": "Original stub 'Lin 2021 retrieval survey' is a book, not on arXiv. Replaced with Contriever, a canonical dense-retrieval baseline.",
    },
    {
        "source_id": "source_004", "round": 1, "arxiv_id": "2002.08909",
        "title": "REALM: Retrieval-Augmented Language Model Pre-Training",
        "mapping": "exact",
    },
    {
        "source_id": "source_005", "round": 1, "arxiv_id": "1704.00051",
        "title": "Reading Wikipedia to Answer Open-Domain Questions",
        "mapping": "exact",
    },
    {
        "source_id": "source_006", "round": 1, "arxiv_id": "2007.01282",
        "title": "Leveraging Passage Retrieval with Language Models",
        "mapping": "exact",
    },
    {
        "source_id": "source_007", "round": 1, "arxiv_id": "2402.19473",
        "title": "Retrieval-Augmented Generation for AI-Generated Content: A Survey",
        "mapping": "replace",
        "note": "Original 'Liu 2022 RAG eval survey' author was vague; replaced with Zhao et al. RAG survey (arXiv 2402.19473) covering RAG evaluation and taxonomy.",
    },
    {
        "source_id": "source_008", "round": 1, "arxiv_id": "2012.04584",
        "title": "Distilling Knowledge from Reader to Retriever for Question Answering",
        "mapping": "replace",
        "note": "Original 'Sachan 2021 joint training' not cleanly on arXiv; replaced with reader->retriever distillation, same joint-optimization theme.",
    },
    {
        "source_id": "source_009", "round": 1, "arxiv_id": "2104.08821",
        "title": "SimCSE: Simple Contrastive Learning of Sentence Embeddings",
        "mapping": "exact",
    },
    {
        "source_id": "source_010", "round": 1, "arxiv_id": "1803.05355",
        "title": "FEVER: a Large-scale Dataset for Fact Extraction and VERification",
        "mapping": "exact",
    },
    # ---------------------------------------------------------------- Round 2
    {
        "source_id": "source_011", "round": 2, "arxiv_id": "2404.16130",
        "title": "From Local to Global: A Graph RAG Approach to Query-Focused Summarization",
        "mapping": "exact",
    },
    {
        "source_id": "source_012", "round": 2, "arxiv_id": "2405.14831",
        "title": "HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models",
        "mapping": "replace",
        "note": "Original 'Wang 2024 Agentic RAG' authors fabricated; replaced with HippoRAG, a canonical agentic memory-RAG.",
    },
    {
        "source_id": "source_013", "round": 2, "arxiv_id": "2112.12870",
        "title": "Measuring Attribution in Natural Language Generation Models",
        "mapping": "approx",
        "note": "Stub named Bohnet/Kamigaito (real attribution researchers); Rashkin et al. is the canonical attribution-evaluation paper.",
    },
    {
        "source_id": "source_014", "round": 2, "arxiv_id": "2310.01061",
        "title": "Reasoning on Graphs (RoG): Faithful and Interpretable Reasoning on Large Language Models",
        "mapping": "replace",
        "note": "Original 'Sun KG-RAG' fabricated; replaced with RoG, a canonical KG+LLM reasoning paper.",
    },
    {
        "source_id": "source_015", "round": 2, "arxiv_id": "2401.15391",
        "title": "MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for Multi-Hop Queries",
        "mapping": "exact",
    },
    {
        "source_id": "source_016", "round": 2, "arxiv_id": "2310.11511",
        "title": "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
        "mapping": "exact",
    },
    {
        "source_id": "source_017", "round": 2, "arxiv_id": "2401.15884",
        "title": "Corrective Retrieval Augmented Generation",
        "mapping": "exact",
    },
    {
        "source_id": "source_018", "round": 2, "arxiv_id": "2309.15217",
        "title": "Ragas: Automated Evaluation of Retrieval Augmented Generation",
        "mapping": "exact",
    },
    {
        "source_id": "source_019", "round": 2, "arxiv_id": "2407.08223",
        "title": "Speculative RAG: Enhancing Retrieval Augmented Generation through Drafting",
        "mapping": "exact",
    },
    {
        "source_id": "source_020", "round": 2, "arxiv_id": "2403.14403",
        "title": "Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models Through Question Complexity",
        "mapping": "exact",
    },
    # ---------------------------------------------------------------- Round 3
    {
        "source_id": "source_021", "round": 3, "arxiv_id": "2407.16833",
        "title": "Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach",
        "mapping": "replace",
        "note": "Original 'Li 2024 RAG vs long-context' fabricated; replaced with Li et al. (EMNLP 2024) canonical RAG-vs-LC comparison (correct id, previously mistyped as 2409.12549 which is a music paper).",
    },
    {
        "source_id": "source_022", "round": 3, "arxiv_id": "2307.03172",
        "title": "Lost in the Middle: How Language Models Use Long Contexts",
        "mapping": "replace",
        "note": "Original 'Chen 2024 long-context bottleneck' fabricated; replaced with the canonical Lost-in-the-Middle paper.",
    },
    {
        "source_id": "source_023", "round": 3, "arxiv_id": "2408.08921",
        "title": "Graph Retrieval-Augmented Generation: A Survey",
        "mapping": "replace",
        "note": "Original 'Zhang 2024 GraphRAG critique' fabricated; replaced with Graph RAG survey that critically contextualizes GraphRAG.",
    },
    {
        "source_id": "source_024", "round": 3, "arxiv_id": "2312.10997",
        "title": "Retrieval-Augmented Generation for Large Language Models: A Survey",
        "mapping": "replace",
        "note": "Original 'Wang 2024 RAG homogenization meta-analysis' fabricated; replaced with Gao et al. RAG survey covering concept proliferation.",
    },
    {
        "source_id": "source_025", "round": 3, "arxiv_id": "2401.14887",
        "title": "The Power of Noise: Redefining Retrieval for RAG Systems",
        "mapping": "replace",
        "note": "Original 'Zhao 2024 edge-case failure' fabricated; replaced with Cuconasu et al. (SIGIR 2024) on noise/edge-case RAG behavior (correct id, previously mistyped as 2401.09201).",
    },
    {
        "source_id": "source_026", "round": 3, "arxiv_id": "2405.07437",
        "title": "Evaluation of Retrieval-Augmented Generation: A Survey",
        "mapping": "replace",
        "note": "Original 'Liu 2024 RAGAS critique' + my earlier guess 'Vorobev 2410.16095' both unverifiable; replaced with this survey on RAG evaluation metrics, which covers reliability/critique of automated eval.",
    },
    {
        "source_id": "source_027", "round": 3, "arxiv_id": "2212.10511",
        "title": "When Not to Trust Language Models: Investigating Effectiveness and Limitations of Parametric and Non-Parametric Memories",
        "mapping": "approx",
        "note": "Stub framed as 'RAG vs fine-tuning'; Mallen et al. is the canonical adaptive-retrieval-by-popularity paper, closely aligned.",
    },
    {
        "source_id": "source_028", "round": 3, "arxiv_id": "2210.02928",
        "title": "Multimodal-RAG (MuRAG)",
        "mapping": "replace",
        "note": "Original 'Chen 2024 multimodal RAG' fabricated; replaced with MuRAG, a canonical multimodal-RAG paper.",
    },
    {
        "source_id": "source_029", "round": 3, "arxiv_id": "2403.10081",
        "title": "DRAGIN: Dynamic Retrieval Augmented Generation Based on the Real-time Information Needs of Large Language Models",
        "mapping": "replace",
        "note": "Original 'Zhang 2024 KB maintenance degradation' is the project's own research topic (no real paper). Replaced with DRAGIN (user-approved), which addresses dynamic retrieval-decision in agent settings.",
    },
    {
        "source_id": "source_030", "round": 3, "arxiv_id": "2211.08411",
        "title": "Large Language Models Struggle to Learn Long-Tail Knowledge",
        "mapping": "exact",
    },
]


def get_manifest() -> list[dict]:
    """Return the full paper manifest (sorted by source_id)."""
    return sorted(PAPER_MANIFEST, key=lambda p: p["source_id"])


def get_by_source(source_id: str) -> dict | None:
    """Look up a manifest entry by source_id."""
    for entry in PAPER_MANIFEST:
        if entry["source_id"] == source_id:
            return entry
    return None
