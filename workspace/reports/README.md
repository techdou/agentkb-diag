# Workspace Reports

This directory holds narrative experiment artifacts (case studies, etc.).

## case_studies.json

Four qualitative case studies illustrating the degradation → diagnosis →
repair cycle of the agent-maintained knowledge base.

**Important — how to read the numbers in these case studies:**

- The case studies are *narrative* documents written to illustrate phenomena
  (duplicate concepts, orphan pages, unsupported-claim cascades, repair
  impact). Specific figures embedded in the prose (e.g. "Jaccard 0.73",
  "cosine 0.81", per-query rank changes) are illustrative of the diagnosis
  method, not recomputed on every load.
- The aggregate round-level metrics they cite (Recall@3 0.85→0.72→0.55→0.78,
  MRR 0.78→0.65→0.48→0.72, citation coverage 0.85→0.62→0.80) match the frozen
  per-round snapshots in `workspace/rounds/*/retrieval_eval.json` and
  `health_report.json`. Those snapshots encode the intended
  degradation-then-repair narrative under per-round corpus isolation.
- The current demo corpus does **not** isolate concepts per round
  (`get_round_concepts` falls back to the full 18-concept index when a round
  lacks its own `concepts.json`). As a result, real-time recomputation after
  the CJK-tokenization fix (M3) yields uniform Recall@3 ≈ 0.98 across all
  rounds. To reproduce the narrative curve, each round needs its own
  concept/claim subset snapshot — a data-modeling task, tracked separately.
- Claim ids referenced (claim_001 … claim_030) are real and live in
  `workspace/index/claims.json`. `claim_020` (GraphRAG vs vector RAG,
  conflicted) stands in for the cascade example; no phantom claim ids remain.

When the per-round corpus isolation is implemented, regenerate
`retrieval_eval.json` and `health_report.json` for each round so the live
metrics match the narrative.
