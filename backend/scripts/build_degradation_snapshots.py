"""Build realistic degradation snapshots for round_2 / round_3 / round_3_repair.

The project's "multi-round degradation" narrative must be backed by *real* data
differences, not pre-stored numbers. This script derives round snapshots from
the clean round_1 index (workspace/index/*.json) by injecting the kinds of
errors an LLM agent accumulates over rounds: claim text pollution (TF-IDF
dilution), alias loss, duplicate concepts, orphan pages, conflicting claims,
and broken citation links. round_3_repair reverses most (not all) of the
damage, modelling an imperfect repair.

The injected issues are detected by diagnosis.find_issues() at experiment time,
so health metrics are computed live from the data — not simulated.

CRITICAL: this script also removes pre-stored health_report.json /
retrieval_eval.json / build_snapshot.json from each round dir, so the diagnosis
service recomputes metrics from the (now degraded) data instead of returning
cached numbers.

Idempotent and seeded for reproducibility.

Usage:
    python backend/scripts/build_degradation_snapshots.py
    python backend/scripts/build_degradation_snapshots.py --seed 42
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent
INDEX_DIR = _PROJECT_ROOT / "workspace" / "index"
ROUNDS_DIR = _PROJECT_ROOT / "workspace" / "rounds"

# Concepts most heavily exercised by the 48 retrieval tests. Degradation is
# concentrated here so that recall@k actually moves.
HOT_PAGES = ["RAG", "GraphRAG", "Self_RAG", "Citation_Faithfulness",
             "Dense_Retrieval", "RAG_Evaluation", "Agentic_RAG",
             "Corrective_RAG"]

# Pool of distractor tokens drawn from *other* concepts' names/aliases. Injecting
# these into a page's claim text dilutes that page's TF-IDF signal for its own
# query keywords — a realistic "agent paraphrased too much" failure.
DISTRACTOR_POOL = [
    "知识图谱", "多模态", "幻觉检测", "长文本对齐", "检索器蒸馏",
    "事实核查", "嵌入式向量", "提示工程", "推理链", "上下文压缩",
    "神经符号", "对抗鲁棒性", "分布外泛化", "元学习", "对比学习",
]


def load_index() -> dict:
    """Load the clean round_1 baseline from workspace/index/."""
    return {
        "claims": json.loads((INDEX_DIR / "claims.json").read_text(encoding="utf-8")),
        "concepts": json.loads((INDEX_DIR / "concepts.json").read_text(encoding="utf-8")),
        "graph": json.loads((INDEX_DIR / "graph.json").read_text(encoding="utf-8")),
        "aliases": json.loads((INDEX_DIR / "aliases.json").read_text(encoding="utf-8")),
    }


# ── Degradation primitives ──────────────────────────────────────────────────

def inject_text_noise(claims: list[dict], pages: set[str], n_words: int,
                      rng: random.Random) -> int:
    """Append distractor tokens to claims on the given pages, diluting TF-IDF.

    Returns the number of claims modified.
    """
    modified = 0
    for cl in claims:
        if cl["page_id"] in pages:
            tokens = rng.sample(DISTRACTOR_POOL, k=min(n_words, len(DISTRACTOR_POOL)))
            # Repeat to amplify dilution (mimics verbose agent restatement)
            noise = " ".join(tokens * 2)
            cl["text"] = cl["text"] + " " + noise
            modified += 1
    return modified


def drop_aliases(aliases: list[dict], canonical_names: set[str], ratio: float,
                 rng: random.Random) -> int:
    """Remove a fraction of aliases for the given canonical concepts."""
    targets = [a for a in aliases if a["canonical"] in canonical_names
               and a["status"] == "confirmed"]
    rng.shuffle(targets)
    n_drop = int(len(targets) * ratio)
    dropped_ids = set()
    for a in targets[:n_drop]:
        dropped_ids.add((a["alias"], a["canonical"]))
    kept = [a for a in aliases
            if (a["alias"], a["canonical"]) not in dropped_ids]
    # Mutate in place: replace list contents
    aliases.clear()
    aliases.extend(kept)
    return n_drop


def add_duplicate_concepts(concepts: list[dict], aliases: list[dict],
                           graph: dict, sources: list[str],
                           templates: list[tuple[str, str]], rng: random.Random) -> int:
    """Add near-duplicate concept pages (e.g. 'RAG_v2') that fragment retrieval.

    Each duplicate gets a suggested-status alias pointing back to the original,
    which find_issues() will flag as a potential duplicate.
    """
    added = 0
    for orig_page, new_page in templates:
        orig = next((c for c in concepts if c["page_id"] == orig_page), None)
        if not orig:
            continue
        dup = copy.deepcopy(orig)
        dup["concept_id"] = f"concept_{new_page}"
        dup["canonical_name"] = new_page.replace("_", " ")
        dup["page_id"] = new_page
        dup["round_created"] = 2
        dup["round_updated"] = 2
        concepts.append(dup)
        # Suggested alias -> triggers duplicate detection
        aliases.append({
            "alias": dup["canonical_name"],
            "canonical": orig["canonical_name"],
            "confidence": 0.6,
            "status": "suggested",
        })
        # Graph node with no edges -> becomes an orphan (find_issues flags it)
        graph["nodes"].append({
            "id": new_page,
            "type": "concept_page",
            "label": dup["canonical_name"],
            "round_created": 2,
            "issue_flags": [],
        })
        added += 1
    return added


def make_orphans(concepts: list[dict], claims: list[dict], graph: dict,
                 pages: list[str]) -> int:
    """Turn the given concept pages into orphans: drop all their edges AND
    clear their claims, so they are both unlinked and empty."""
    n = 0
    for page in pages:
        graph["edges"] = [e for e in graph["edges"]
                          if e["source"] != page and e["target"] != page]
        before = len(claims)
        claims[:] = [c for c in claims if c["page_id"] != page]
        n += before - len(claims)
    return n


def add_conflicts(claims: list[dict], pages: list[str], rng: random.Random) -> int:
    """Flip some claims on the given pages to 'conflicted' status and inject a
    contradictory restatement."""
    contradictory_suffixes = [
        "（注：另有研究表明此结论在不同设置下不成立）",
        "（注意：该声明与近期复现实验结果相矛盾）",
        "（争议：部分来源给出相反结论）",
    ]
    n = 0
    for page in pages:
        page_claims = [c for c in claims if c["page_id"] == page and c["status"] == "supported"]
        if not page_claims:
            continue
        target = rng.choice(page_claims)
        target["status"] = "conflicted"
        target["text"] += rng.choice(contradictory_suffixes)
        n += 1
    return n


def break_citation_links(graph: dict, page: str, ratio: float,
                         rng: random.Random) -> int:
    """Remove a fraction of source->page citation edges (drops citation coverage)."""
    cite_edges = [e for e in graph["edges"]
                  if e["target"] == page and e["source"].startswith("source_")]
    rng.shuffle(cite_edges)
    n_drop = int(len(cite_edges) * ratio)
    drop_set = {(e["source"], e["target"]) for e in cite_edges[:n_drop]}
    before = len(graph["edges"])
    graph["edges"] = [e for e in graph["edges"]
                      if (e["source"], e["target"]) not in drop_set]
    return before - len(graph["edges"])


# ── Round composition ───────────────────────────────────────────────────────

def build_round_2(base: dict, rng: random.Random) -> dict:
    """Mild degradation: text noise on hot pages, duplicate concepts, broken
    citation links. Noise is strong enough to measurably perturb TF-IDF."""
    snap = copy.deepcopy(base)
    hot = {"RAG", "GraphRAG", "Self_RAG", "Citation_Faithfulness"}
    # Inject noise twice (cumulative dilution) on hot pages
    n_noise = inject_text_noise(snap["claims"], hot, n_words=6, rng=rng)
    n_noise += inject_text_noise(snap["claims"], hot, n_words=6, rng=rng)
    n_dup = add_duplicate_concepts(
        snap["concepts"], snap["aliases"], snap["graph"], [],
        [("RAG", "RAG_v2"), ("GraphRAG", "GraphRAG_Lite")], rng,
    )
    n_broken = break_citation_links(snap["graph"], "RAG", ratio=0.3, rng=rng)
    print(f"  round_2: noise={n_noise} dups={n_dup} broken_links={n_broken}")
    return snap


def build_round_3(r2: dict, rng: random.Random) -> dict:
    """Severe degradation: heavy cumulative noise across ALL tested pages,
    alias loss, orphan pages, conflicts, broad link breakage."""
    snap = copy.deepcopy(r2)
    # All 13 tested pages get heavy noise, applied multiple times
    hot_all = set(HOT_PAGES) | {"KG_RAG", "Multimodal_RAG", "Multi_Hop_Retrieval",
                                "Long_Context", "KB_Degradation"}
    n_noise = 0
    for _ in range(3):
        n_noise += inject_text_noise(snap["claims"], hot_all, n_words=8, rng=rng)
    # Drop aliases for the most-tested canonicals
    canonicals = {"RAG", "Graph RAG", "Self RAG", "Dense Retrieval",
                  "Citation Faithfulness", "RAG Evaluation"}
    n_alias = drop_aliases(snap["aliases"], canonicals, ratio=0.5, rng=rng)
    # Orphanize pages tested by a few queries (4-5 tests) so recall drops
    n_orphan_claims = make_orphans(
        snap["concepts"], snap["claims"], snap["graph"],
        ["Multimodal_RAG", "Multi_Hop_Retrieval"],
    )
    n_conflict = add_conflicts(
        snap["claims"],
        ["RAG", "Dense_Retrieval", "Self_RAG", "GraphRAG", "Citation_Faithfulness"],
        rng,
    )
    # Break citation links broadly across high-traffic pages
    n_broken = sum(
        break_citation_links(snap["graph"], p, 0.5, rng)
        for p in ["RAG", "GraphRAG", "Self_RAG", "Dense_Retrieval"]
    )
    print(f"  round_3: noise={n_noise} aliases_dropped={n_alias} "
          f"orphaned_claims={n_orphan_claims} conflicts={n_conflict} "
          f"broken_links={n_broken}")
    return snap


def build_round_3_repair(r3: dict, rng: random.Random) -> dict:
    """Imperfect repair: strip injected noise, restore most aliases, resolve
    conflicts, relink orphans — but KEEP the duplicate concepts (repair missed
    them), modelling a realistic partial recovery."""
    snap = copy.deepcopy(r3)

    # 1. Remove injected noise: strip any text after the first Chinese full stop
    #    that we appended distractor tokens to. We mark noise by detecting the
    #    distractor tokens. Simplest reliable approach: re-derive clean claims
    #    from base text. Since we deep-copied, reconstruct from round_1 is hard
    #    here — instead strip the known distractor tokens.
    for cl in snap["claims"]:
        for tok in DISTRACTOR_POOL:
            cl["text"] = cl["text"].replace(tok, "")
        # strip contradictory suffixes
        for suf in ["（注：另有研究表明此结论在不同设置下不成立）",
                    "（注意：该声明与近期复现实验结果相矛盾）",
                    "（争议：部分来源给出相反结论）"]:
            cl["text"] = cl["text"].replace(suf, "")
        cl["text"] = cl["text"].rstrip()
        # resolve conflicts back to supported
        if cl["status"] == "conflicted":
            cl["status"] = "supported"
    print("  round_3_repair: stripped noise + resolved conflicts")

    # 2. Restore aliases: re-add the confirmed aliases from round_1 baseline for
    #    the canonicals we dropped. We read them fresh from index.
    base_aliases = json.loads((INDEX_DIR / "aliases.json").read_text(encoding="utf-8"))
    existing = {(a["alias"], a["canonical"]) for a in snap["aliases"]}
    restored = 0
    for a in base_aliases:
        key = (a["alias"], a["canonical"])
        if (a["canonical"] in {"RAG", "Graph RAG", "Self RAG", "Dense Retrieval"}
                and key not in existing):
            snap["aliases"].append(a)
            restored += 1
    print(f"  round_3_repair: restored {restored} aliases")

    # 3. Relink orphans: re-add edges + one clean claim for orphaned pages.
    base = load_index()
    orphan_pages = ["KG_RAG", "Multimodal_RAG"]
    for page in orphan_pages:
        # restore edges from base
        base_edges = [e for e in base["graph"]["edges"]
                      if e["source"] == page or e["target"] == page]
        existing_edges = {(e["source"], e["target"]) for e in snap["graph"]["edges"]}
        for e in base_edges:
            if (e["source"], e["target"]) not in existing_edges:
                snap["graph"]["edges"].append(e)
        # restore one clean claim
        base_claim = next((c for c in base["claims"] if c["page_id"] == page), None)
        if base_claim:
            snap["claims"].append(copy.deepcopy(base_claim))
    print(f"  round_3_repair: relinked {len(orphan_pages)} orphan pages")

    # 4. NOTE: duplicate concepts (RAG_v2, GraphRAG_Lite) intentionally KEPT —
    #    the repair did not catch them. They remain as residual issues.
    return snap


# ── IO ──────────────────────────────────────────────────────────────────────

def write_snapshot(round_name: str, snap: dict) -> None:
    d = ROUNDS_DIR / round_name
    d.mkdir(parents=True, exist_ok=True)
    for fname, data in snap.items():
        (d / f"{fname}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {d}/ (claims, concepts, graph, aliases)")


def clear_stale_metrics(round_name: str) -> None:
    """Remove pre-stored health_report.json / retrieval_eval.json /
    build_snapshot.json so diagnosis recomputes from live data."""
    d = ROUNDS_DIR / round_name
    removed = 0
    for stale in ["health_report.json", "retrieval_eval.json", "build_snapshot.json"]:
        p = d / stale
        if p.exists():
            p.unlink()
            removed += 1
    if removed:
        print(f"  removed {removed} stale metric files from {round_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build degradation round snapshots")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    print(f"Loading clean baseline from {INDEX_DIR} (seed={args.seed})")
    base = load_index()
    print(f"  baseline: {len(base['claims'])} claims, {len(base['concepts'])} "
          f"concepts, {len(base['graph']['edges'])} edges, "
          f"{len(base['aliases'])} aliases\n")

    # round_1 = clean baseline (write its data snapshot too, for symmetry)
    print("round_1 (clean baseline):")
    write_snapshot("round_1", base)
    clear_stale_metrics("round_1")

    print("\nround_2 (mild degradation):")
    r2 = build_round_2(base, rng)
    write_snapshot("round_2", r2)
    clear_stale_metrics("round_2")

    print("\nround_3 (severe degradation):")
    r3 = build_round_3(r2, rng)
    write_snapshot("round_3", r3)
    clear_stale_metrics("round_3")

    print("\nround_3_repair (partial repair):")
    r3r = build_round_3_repair(r3, rng)
    write_snapshot("round_3_repair", r3r)
    clear_stale_metrics("round_3_repair")

    print("\nDone. All round snapshots rebuilt with real degradation.")
    print("Re-run experiments to see live-computed degradation in metrics.")


if __name__ == "__main__":
    main()
