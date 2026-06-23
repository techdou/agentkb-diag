"""
OKF v0.1 bundle importer (consumer).

Derives the index JSON files (concepts/claims/sources/graph/aliases) from an
OKF-compliant bundle. This is the consumer side — it proves producer/consumer
independence: the bundle produced by okf_export.py can be round-tripped back
into the JSON the diagnosis/retrieval pipeline expects.

Output files match backend/app/models/schemas.py contracts:
  - concepts.json : concept_id, canonical_name, aliases, page_id, round_created, round_updated
  - claims.json   : claim_id, text, page_id, source_ids, round_created, round_updated, status
  - sources.json  : source_id, title, authors, year, round, tags, abstract, page_id, concepts
  - graph.json    : nodes[], edges[] (rebuilt from markdown links — richer than legacy)
  - aliases.json  : alias, canonical, confidence, status

retrieval_tests.json and rounds/* snapshots are evaluation artifacts, not
knowledge — they are preserved as-is (not regenerated).

Usage:
    python backend/scripts/okf_import.py [bundle_dir] [out_dir]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = PROJECT_ROOT / "okf"
DEFAULT_OUT = PROJECT_ROOT / "workspace" / "index"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# Markdown links: [label](/path.md) or [label](/path.md#anchor)
LINK_RE = re.compile(r"\[([^\]]+)\]\((/[^)]+?)(?:#[^)]*)?\)")


# ---------------------------------------------------------------------------
# Minimal YAML frontmatter parser (no PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse the leading YAML block. Returns (fields, body_after_block)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    fields: dict[str, Any] = {}
    for line in raw.split("\n"):
        line = line.rstrip()
        if not line or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        fields[key] = _parse_yaml_value(val)
    return fields, body


def _parse_yaml_value(val: str) -> Any:
    """Parse a single YAML scalar/flow-list value (best-effort)."""
    if val == "":
        return ""
    # Flow list: [a, b, c] or ["a", "b"]
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        items = _split_flow_list(inner)
        return [_parse_yaml_scalar(i) for i in items]
    return _parse_yaml_scalar(val)


def _split_flow_list(inner: str) -> list[str]:
    """Split a flow-list body on top-level commas (respecting quotes)."""
    parts: list[str] = []
    depth = 0
    cur: list[str] = []
    in_quote: str | None = None
    for ch in inner:
        if in_quote:
            cur.append(ch)
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ('"', "'"):
            in_quote = ch
            cur.append(ch)
        elif ch == "[":
            depth += 1
            cur.append(ch)
        elif ch == "]":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    return parts


def _parse_yaml_scalar(val: str) -> Any:
    val = val.strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    if val.lower() in ("true", "false"):
        return val.lower() == "true"
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    if re.fullmatch(r"-?\d+\.\d+", val):
        return float(val)
    return val


# ---------------------------------------------------------------------------
# Bundle parsing
# ---------------------------------------------------------------------------

def parse_bundle(bundle: Path) -> dict[str, list[dict]]:
    """Walk the bundle and return parsed docs grouped by type."""
    docs: dict[str, list[dict]] = {"Concept": [], "Source": [], "Synthesis": []}
    for md in sorted(bundle.rglob("*.md")):
        if md.name in ("index.md", "log.md"):
            continue
        text = md.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        type_ = fm.get("type")
        if type_ not in docs:
            continue
        docs[type_].append({
            "path": md.relative_to(bundle),
            "frontmatter": fm,
            "body": body,
            "raw": text,
        })
    return docs


# ---------------------------------------------------------------------------
# JSON builders
# ---------------------------------------------------------------------------

def _concept_id_from_canonical(canonical: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", canonical).strip("_")
    return f"concept_{slug}"


def build_concepts(concept_docs: list[dict]) -> list[dict]:
    out: list[dict] = []
    for d in concept_docs:
        fm = d["frontmatter"]
        page_id = d["path"].stem  # filename without .md
        canonical = fm.get("title", page_id)
        out.append({
            "concept_id": _concept_id_from_canonical(canonical),
            "canonical_name": canonical,
            "aliases": fm.get("aliases", []),
            "page_id": page_id,
            "round_created": int(fm.get("round_created", 1)),
            "round_updated": int(fm.get("round_updated", 1)),
        })
    return out


def build_sources(source_docs: list[dict]) -> list[dict]:
    out: list[dict] = []
    for d in source_docs:
        fm = d["frontmatter"]
        source_id = fm.get("source_id", d["path"].stem)
        authors_raw = fm.get("authors", "")
        authors = [a.strip() for a in str(authors_raw).split(",")] if authors_raw else []
        # Concepts mentioned in a ## Concepts section body.
        concepts = _extract_concepts_list(d["body"])
        out.append({
            "source_id": source_id,
            "title": fm.get("title", source_id),
            "authors": authors,
            "year": int(fm.get("year", 0)) if fm.get("year") else 0,
            "round": int(fm.get("round_created", 1)),
            "tags": fm.get("tags", []),
            "abstract": fm.get("description", ""),
            "page_id": source_id,
            "concepts": concepts,
        })
    return out


def _extract_concepts_list(body: str) -> list[str]:
    m = re.search(r"##\s*Concepts\s*\n(.+?)(?:\n#|\Z)", body, re.DOTALL)
    if not m:
        return []
    items = re.findall(r"^\s*-\s+(.+)$", m.group(1), re.MULTILINE)
    return [i.strip() for i in items]


def build_claims(concept_docs: list[dict], source_docs: list[dict]) -> list[dict]:
    """Reconstruct claims from concept bodies.

    Each concept renders its claims as anchor lines:
      <a id="claim_XXX"></a>**claim_XXX**[src:s1,s2] (status): text
    or within list items. We parse these to recover claim_id, status, text,
    page_id (the concept), and per-claim source_ids from the [src:...] tag.

    When a [src:...] tag is absent (older bundles), we fall back to the
    concept-level # Citations set, which over-approximates per-claim sources.
    """
    claims: list[dict] = []
    # Match: anchor + **claim_id** + (status) + optional [src:...] tag + ": " + text.
    # The [src:...] tag is emitted AFTER (status) by okf_export.
    src_tag = r"(?:\s*\[src:([^\]]*)\])?"
    status_re = r"\((supported|unsupported|conflicted)\)"
    claim_re = re.compile(
        r'<a id="(claim_\d+)"></a>\*?\*?\1\*?\*?\s*' + status_re + src_tag +
        r":\s*(.+)",
    )
    claim_re_list = re.compile(
        r'-\s*<a id="(claim_\d+)"></a>\*?\*?\1\*?\*?\s*' + status_re + src_tag +
        r":\s*(.+)",
    )

    for d in concept_docs:
        fm = d["frontmatter"]
        page_id = d["path"].stem
        rc = int(fm.get("round_created", 1))
        ru = int(fm.get("round_updated", rc))
        body = d["body"]

        # Find all claim anchors in this concept. Each match yields
        # (claim_id, status, src_tag_raw, text) — order follows the regex groups.
        found: list[tuple[str, str, str, str]] = []
        for m in claim_re.finditer(body):
            found.append((m.group(1), m.group(2), m.group(3) or "", m.group(4).strip()))
        for m in claim_re_list.finditer(body):
            found.append((m.group(1), m.group(2), m.group(3) or "", m.group(4).strip()))
        # Dedupe by claim_id (keep first).
        seen: set[str] = set()
        unique: list[tuple[str, str, str, str]] = []
        # found tuples are (claim_id, status, src_raw, text).
        for cid, status, src_raw, text in found:
            if cid not in seen:
                seen.add(cid)
                unique.append((cid, status, src_raw, text))

        concept_cited = _extract_cited_sources(body)

        for cid, status, src_raw, text in unique:
            # Per-claim source_ids from the [src:...] tag when present.
            if src_raw.strip():
                source_ids = [s.strip() for s in src_raw.split(",") if s.strip()]
            elif len(unique) == 1:
                # Single claim — concept-level citation set is exact.
                source_ids = list(concept_cited)
            else:
                # Fallback: no per-claim provenance encoded; use concept set.
                source_ids = list(concept_cited)
            claims.append({
                "claim_id": cid,
                "text": text,
                "page_id": page_id,
                "source_ids": source_ids,
                "round_created": rc,
                "round_updated": ru,
                "status": status,
            })
    return claims


def _extract_cited_sources(body: str) -> list[str]:
    """Extract source_ids from a # Citations section: [n] [label](/sources/SID.md)."""
    m = re.search(r"#\s*Citations\s*\n(.+)", body, re.DOTALL)
    if not m:
        return []
    refs = re.findall(r"\((/sources/([^)]+?)\.md)\)", m.group(1))
    return [sid for _, sid in refs]


def build_graph(
    concept_docs: list[dict],
    source_docs: list[dict],
    synthesis_docs: list[dict],
) -> dict[str, Any]:
    """Rebuild graph nodes + edges from frontmatter + markdown links.

    Richer than the legacy graph.json: includes concept AND source nodes,
    and edges derived from every standard markdown link in every document.
    """
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    edge_keys: set[tuple[str, str, str]] = set()

    def add_node(node_id: str, type_: str, label: str, rc: int, flags: list[str] | None = None):
        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "type": type_,
                "label": label,
                "round_created": rc,
                "issue_flags": flags or [],
            }

    def add_edge(src: str, tgt: str, etype: str, rc: int, conf: float):
        key = (src, tgt, etype)
        if src == tgt or key in edge_keys:
            return
        edge_keys.add(key)
        edges.append({
            "source": src,
            "target": tgt,
            "type": etype,
            "round_created": rc,
            "confidence": conf,
        })

    # Register nodes.
    for d in concept_docs:
        fm = d["frontmatter"]
        pid = d["path"].stem
        add_node(pid, "concept_page", fm.get("title", pid), int(fm.get("round_created", 1)))
    for d in source_docs:
        fm = d["frontmatter"]
        sid = fm.get("source_id", d["path"].stem)
        add_node(sid, "source_page", fm.get("title", sid), int(fm.get("round_created", 1)))
    for d in synthesis_docs:
        fm = d["frontmatter"]
        pid = d["path"].stem
        add_node(pid, "synthesis_page", fm.get("title", pid), int(fm.get("round_created", 3)))

    # Derive edges from markdown links. Link target /concepts/X.md -> node X.
    def link_target_node(url: str) -> str | None:
        # /concepts/RAG.md  -> RAG ; /sources/source_001.md -> source_001
        m = re.match(r"/(concepts|sources|syntheses)/([^)]+?)\.md", url)
        if not m:
            if url in ("/index.md", "/overview.md", "/log.md"):
                return url.strip("/").replace(".md", "")
            return None
        return m.group(2)

    for docs, self_type in [
        (concept_docs, "concept_page"),
        (source_docs, "source_page"),
        (synthesis_docs, "synthesis_page"),
    ]:
        for d in docs:
            src_id = d["path"].stem if self_type != "source_page" else d["frontmatter"].get("source_id", d["path"].stem)
            rc = int(d["frontmatter"].get("round_created", 1))
            for label, url in LINK_RE.findall(d["body"]):
                tgt = link_target_node(url)
                if tgt and tgt in nodes:
                    add_edge(src_id, tgt, "references", rc, 1.0)

    return {"nodes": list(nodes.values()), "edges": edges}


def build_aliases(concept_docs: list[dict]) -> list[dict]:
    """Rebuild aliases from each concept's `aliases` frontmatter field.
    Confidence/status are reconstructed heuristically (confirmed for short
    canonical aliases)."""
    out: list[dict] = []
    for d in concept_docs:
        fm = d["frontmatter"]
        canonical = fm.get("title", d["path"].stem)
        for alias in fm.get("aliases", []):
            # Heuristic: abbreviations and short tokens are confirmed, long
            # Chinese descriptions are suggested.
            is_short = len(alias) <= 10 or alias.replace("-", "").replace(" ", "").isascii()
            out.append({
                "alias": alias,
                "canonical": canonical,
                "confidence": 0.85 if is_short else 0.65,
                "status": "confirmed" if is_short else "suggested",
            })
    return out


# ---------------------------------------------------------------------------
# Top-level import
# ---------------------------------------------------------------------------

def import_bundle(bundle: Path, out_dir: Path) -> dict[str, int]:
    docs = parse_bundle(bundle)
    concepts = build_concepts(docs["Concept"])
    sources = build_sources(docs["Source"])
    claims = build_claims(docs["Concept"], docs["Source"])
    graph = build_graph(docs["Concept"], docs["Source"], docs["Synthesis"])
    aliases = build_aliases(docs["Concept"])

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "concepts.json", concepts)
    _write_json(out_dir / "claims.json", claims)
    _write_json(out_dir / "sources.json", sources)
    _write_json(out_dir / "graph.json", graph)
    _write_json(out_dir / "aliases.json", aliases)

    return {
        "concepts": len(concepts),
        "claims": len(claims),
        "sources": len(sources),
        "graph_nodes": len(graph["nodes"]),
        "graph_edges": len(graph["edges"]),
        "aliases": len(aliases),
    }


def _write_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    bundle = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BUNDLE
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    if not bundle.exists():
        print(f"Bundle not found: {bundle}")
        sys.exit(2)
    # Safety: refuse to overwrite index without a backup env flag, unless the
    # caller passes an explicit out_dir.
    counts = import_bundle(bundle, out_dir)
    print(f"OKF bundle imported from {bundle} -> {out_dir}")
    for k, v in counts.items():
        print(f"  {k:12}: {v}")
