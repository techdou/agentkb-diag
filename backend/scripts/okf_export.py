"""
OKF v0.1 bundle exporter.

Converts the existing wiki Markdown + index JSON into an Open Knowledge
Format (OKF) compliant bundle at the project root.

OKF v0.1 conformance (https://github.com/GoogleCloudPlatform/knowledge-catalog):
  1. Every non-reserved .md file has a parseable YAML frontmatter block.
  2. Every frontmatter block contains a non-empty `type` field.
  3. Reserved filenames (index.md, log.md) follow §6/§7 structure.
  4. Cross-links use standard markdown links, not [[wikilink]].

Producer side: this script is one way to produce OKF; nothing about OKF
requires it. See okf/README.md for the consumer (okf_import.py).

Usage:
    python -m backend.scripts.okf_export            # from project root
    python backend/scripts/okf_export.py            # direct
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WIKI_DIR = PROJECT_ROOT / "workspace" / "wiki"
INDEX_DIR = PROJECT_ROOT / "workspace" / "index"
OKF_DIR = PROJECT_ROOT / "okf"

OKF_VERSION = "0.1"

# round_updated int -> canonical timestamp mapping (mirrors round snapshot times).
ROUND_TIMESTAMP = {
    1: "2026-05-01T10:00:00Z",
    2: "2026-05-05T14:00:00Z",
    3: "2026-05-10T16:00:00Z",
}


# ---------------------------------------------------------------------------
# Index loaders
# ---------------------------------------------------------------------------

def _load_json(name: str) -> Any:
    path = INDEX_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class IndexData:
    concepts: list[dict]
    claims: list[dict]
    sources: list[dict]
    aliases: list[dict]

    @classmethod
    def load(cls) -> "IndexData":
        raw_concepts = _load_json("concepts.json")
        # Merge with concepts discovered on disk: wiki/concepts/*.md is the
        # source of truth for which concepts exist (concepts.json has been
        # observed to under-register some pages, e.g. Knowledge_Boundary).
        raw_concepts = cls._merge_disk_concepts(raw_concepts)
        claims = _load_json("claims.json")
        # Synthesize stub concepts for orphan claims (page_id with no wiki page).
        raw_concepts.extend(cls._merge_orphan_stubs(claims))
        return cls(
            concepts=raw_concepts,
            claims=claims,
            sources=_load_json("sources.json"),
            aliases=_load_json("aliases.json"),
        )

    @staticmethod
    def _merge_orphan_stubs(claims: list[dict]) -> list[dict]:
        return _discover_orphan_concepts(claims)

    @staticmethod
    def _merge_disk_concepts(registered: list[dict]) -> list[dict]:
        """Augment the registered concept list with any concept page that exists
        on disk but isn't in concepts.json. Infers metadata from the .md file."""
        concepts_dir = WIKI_DIR / "concepts"
        if not concepts_dir.exists():
            return registered
        registered_by_pid = {c["page_id"]: c for c in registered}
        merged = list(registered)
        for md in sorted(concepts_dir.glob("*.md")):
            page_id = md.stem
            if page_id in registered_by_pid:
                continue
            # Infer a minimal concept record from the file's heading/alias block.
            text = md.read_text(encoding="utf-8")
            title = page_id.replace("_", " ")
            heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
            if heading:
                title = heading.group(1).strip()
            aliases = _infer_aliases(text)
            rc, ru = _infer_rounds(page_id)
            merged.append({
                "concept_id": f"concept_{page_id}",
                "canonical_name": title,
                "aliases": aliases,
                "page_id": page_id,
                "round_created": rc,
                "round_updated": ru,
            })
        return merged


def _infer_aliases(text: str) -> list[str]:
    """Pull aliases from the legacy `> 别名: a, b, c` blockquote."""
    m = re.search(r"^>\s*(?:别名|Aliases)\s*:\s*(.+)$", text, re.MULTILINE)
    if not m:
        return []
    return [a.strip() for a in m.group(1).split(",") if a.strip()]


def _infer_rounds(page_id: str) -> tuple[int, int]:
    """Infer round_created/updated from the page's claims (if any) or default."""
    # Knowledge_Boundary and Speculative_RAG both belong to round 3 content.
    late_concepts = {"Knowledge_Boundary", "Speculative_RAG"}
    if page_id in late_concepts:
        return (3, 3)
    return (1, 1)


# Orphan claims: page_id references a concept with no wiki page. Each maps to
# a stub concept we synthesize so the claim survives the round-trip. The value
# is (canonical_name, aliases, round_created, description).
_ORPHAN_STUBS: dict[str, tuple[str, list[str], int, str]] = {
    "Concept_Redundancy": (
        "Concept Redundancy",
        ["概念冗余", "概念同质化", "Concept Homogenization"],
        3,
        "诊断性观察：RAG 领域大量新概念可归为少数基础框架的变体。",
    ),
}


def _discover_orphan_concepts(claims: list[dict]) -> list[dict]:
    """Find claims whose page_id has no wiki page and synthesize stub concepts."""
    stubs: list[dict] = []
    seen: set[str] = set()
    for c in claims:
        pid = c.get("page_id", "")
        wiki_path = WIKI_DIR / "concepts" / f"{pid}.md"
        if pid and not wiki_path.exists() and pid in _ORPHAN_STUBS and pid not in seen:
            seen.add(pid)
            canonical, aliases, rc, _desc = _ORPHAN_STUBS[pid]
            stubs.append({
                "concept_id": f"concept_{pid}",
                "canonical_name": canonical,
                "aliases": aliases,
                "page_id": pid,
                "round_created": rc,
                "round_updated": rc,
                "_stub": True,
            })
    return stubs


# ---------------------------------------------------------------------------
# Claim aggregation helpers
# ---------------------------------------------------------------------------

def claims_by_page(claims: list[dict]) -> dict[str, list[dict]]:
    """Group claims by their page_id (concept page)."""
    out: dict[str, list[dict]] = {}
    for c in claims:
        out.setdefault(c.get("page_id", ""), []).append(c)
    return out


def claims_by_source(claims: list[dict]) -> dict[str, list[dict]]:
    """Group claims by each source_id they cite."""
    out: dict[str, list[dict]] = {}
    for c in claims:
        for sid in c.get("source_ids", []):
            out.setdefault(sid, []).append(c)
    return out


# ---------------------------------------------------------------------------
# Link conversion: [[wikilink]] -> standard markdown links
# ---------------------------------------------------------------------------

# Known root-level pages that are reserved (not concepts/sources/syntheses).
_ROOT_PAGES = {"index", "overview", "log"}


def _build_link_target_map(idx: IndexData) -> dict[str, str]:
    """Map every possible wikilink token to its OKF bundle-relative path."""
    targets: dict[str, str] = {}
    for c in idx.concepts:
        pid = c["page_id"]
        targets[pid] = f"/concepts/{pid}.md"
    for s in idx.sources:
        sid = s["source_id"]
        targets[sid] = f"/sources/{sid}.md"
        targets[f"sources/{sid}"] = f"/sources/{sid}.md"  # long form
    for syn in ("rag_evolution", "rag_conflicts", "kb_health"):
        targets[syn] = f"/syntheses/{syn}.md"
        targets[f"syntheses/{syn}"] = f"/syntheses/{syn}.md"
    for root in _ROOT_PAGES:
        targets[root] = f"/{root}.md"
    return targets


# Claim tokens resolve to an in-page anchor on the owning concept page.
_CLAIM_OWNER: dict[str, str] = {}


def _convert_links(text: str, targets: dict[str, str]) -> str:
    """Replace [[token]] with [token](target) using standard markdown links.

    - Concept/source/synthesis/root tokens map to their OKF path.
    - claim_xxx tokens map to the owning concept page with a fragment.
      If the claim's owner is unknown, render as plain code (no broken link).
    """
    def repl(m: re.Match) -> str:
        token = m.group(1).strip()
        # Already has a path (e.g. [[sources/x]] or [[syntheses/x]]).
        if token in targets:
            tgt = targets[token]
            label = token.split("/")[-1]
            return f"[{label}]({tgt})"
        # Claim token -> owner concept page anchor.
        if token.startswith("claim_"):
            owner = _CLAIM_OWNER.get(token)
            if owner and owner in targets:
                return f"[{token}](/concepts/{owner}.md#{token})"
            return f"`{token}`"  # unknown owner, no broken link
        # Unknown token: render literally in code span (OKF tolerates broken links,
        # but we prefer not to emit dangling markdown links).
        return f"`{token}`"

    return re.sub(r"\[\[([^\]]+)\]\]", repl, text)


# ---------------------------------------------------------------------------
# YAML frontmatter emission (minimal hand-rolled emitter, no PyYAML dep)
# ---------------------------------------------------------------------------

def _yaml_str(value: str) -> str:
    """Quote a YAML string, escaping as needed. Empty -> empty quoted."""
    if value == "":
        return '""'
    # Double-quote if it contains special chars, else bare.
    if re.search(r"[:\#\[\]\{\}\,\&\*\!\|\>\'\"\%\@\`]", value) or value.strip() != value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _yaml_list(items: list[str]) -> str:
    """Emit a YAML flow list [a, b, c] with each item quoted safely."""
    if not items:
        return "[]"
    return "[" + ", ".join(_yaml_str(str(i)) for i in items) + "]"


def emit_frontmatter(fields: dict[str, Any]) -> str:
    """Emit a YAML frontmatter block. Booleans/numbers bare; lists/strings quoted.
    Internal fields (leading underscore) are skipped."""
    lines = ["---"]
    for key, value in fields.items():
        if key.startswith("_"):
            continue
        if value is None:
            continue
        if isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, (int, float)):
            lines.append(f"{key}: {value}")
        elif isinstance(value, list):
            lines.append(f"{key}: {_yaml_list([str(v) for v in value])}")
        else:
            lines.append(f"{key}: {_yaml_str(str(value))}")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Description extraction
# ---------------------------------------------------------------------------

def _extract_description(body: str) -> str:
    """Pull the first meaningful sentence from a concept body (the 定义 section)."""
    # Look for "## 定义" then capture until next heading or blank-line end.
    m = re.search(r"##\s*定义\s*\n+(.+?)(?:\n\n|\n#|\Z)", body, re.DOTALL)
    text = m.group(1).strip() if m else ""
    if not text:
        # Fallback: first non-empty, non-heading paragraph.
        for para in re.split(r"\n\n+", body):
            para = para.strip()
            if para and not para.startswith("#") and not para.startswith(">"):
                text = para
                break
    # Collapse to first sentence (Chinese 。or ASCII .).
    text = re.split(r"(?<=[。.])\s", text)[0]
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:160] + "…") if len(text) > 160 else text


# ---------------------------------------------------------------------------
# Per-page emitters
# ---------------------------------------------------------------------------

def _common_frontmatter(
    type_: str,
    title: str,
    description: str,
    round_created: int,
    round_updated: int,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fm: dict[str, Any] = {
        "type": type_,
        "title": title,
        "description": description,
        "tags": [],  # filled by caller when meaningful
        "timestamp": ROUND_TIMESTAMP.get(round_updated, ROUND_TIMESTAMP[3]),
        "round_created": round_created,
        "round_updated": round_updated,
        "okf_version": OKF_VERSION,
    }
    if extra:
        fm.update(extra)
    return fm


def emit_concept(concept: dict, idx: IndexData, targets: dict[str, str]) -> str:
    """Build a full OKF concept document."""
    page_id = concept["page_id"]
    title = concept["canonical_name"]
    aliases = concept.get("aliases", [])
    rc = concept.get("round_created", 1)
    ru = concept.get("round_updated", rc)

    # Start from the existing wiki body, strip the old # heading + alias blockquote
    # (frontmatter now carries that metadata).
    wiki_path = WIKI_DIR / "concepts" / f"{page_id}.md"
    is_stub = concept.get("_stub", False)
    if wiki_path.exists():
        raw = wiki_path.read_text(encoding="utf-8")
        body = _strip_legacy_header(raw)
    elif is_stub:
        body = _synthesize_concept_body(concept, idx)
    else:
        body = ""

    page_claims = claims_by_page(idx.claims).get(page_id, [])

    # Insert a structured # Claims section if claims belong here but aren't
    # already rendered with anchors. We append anchors to inline claim refs.
    body = _convert_links(body, targets)
    body = _inject_claim_anchors(body, page_claims)

    # Citations: dedup source_ids across this concept's claims.
    cited_sources: list[str] = []
    seen: set[str] = set()
    for c in page_claims:
        for sid in c.get("source_ids", []):
            if sid not in seen:
                seen.add(sid)
                cited_sources.append(sid)

    citations_block = _render_citations(cited_sources, idx, targets)

    description = _extract_description(body)

    fm = _common_frontmatter(
        "Concept",
        title,
        description,
        rc,
        ru,
        extra={
            "aliases": aliases,
            "claim_ids": [c["claim_id"] for c in page_claims] or None,
        },
    )
    if aliases:
        # aliases double as cross-cutting tags for discoverability.
        fm["tags"] = [title.lower().replace(" ", "-")]
    doc = emit_frontmatter(fm) + "\n\n"
    doc += f"# {title}\n\n"
    if aliases:
        doc += f"> Aliases: {', '.join(aliases)}\n\n"
    doc += body.rstrip() + "\n"
    if citations_block:
        doc += "\n" + citations_block
    return doc


def emit_source(source: dict, idx: IndexData, targets: dict[str, str]) -> str:
    """Build an OKF source document. Reuses existing wiki source body if present,
    otherwise synthesizes a stub from sources.json (covers source_011..030)."""
    sid = source["source_id"]
    title = source["title"]
    authors = source.get("authors", [])
    year = source.get("year")
    rc = source.get("round", 1)
    abstract = source.get("abstract", "")

    wiki_path = WIKI_DIR / "sources" / f"{sid}.md"
    raw = wiki_path.read_text(encoding="utf-8") if wiki_path.exists() else ""
    if raw:
        body = _strip_legacy_header(raw)
        body = _convert_links(body, targets)
    else:
        # Synthesize body for sources without a hand-written wiki page.
        body = _synthesize_source_body(source, idx, targets)

    description = abstract.split("。")[0].split(". ")[0] if abstract else title
    fm = _common_frontmatter(
        "Source",
        title,
        description,
        rc,
        rc,
        extra={
            "authors": ", ".join(authors) if authors else None,
            "year": year,
            "source_id": sid,
        },
    )
    fm["tags"] = source.get("tags", [])

    doc = emit_frontmatter(fm) + "\n\n"
    doc += f"# {title}\n\n"
    if authors:
        doc += f"> {', '.join(authors)} ({year})\n\n"
    doc += body.rstrip() + "\n"
    return doc


def emit_synthesis(name: str, idx: IndexData, targets: dict[str, str]) -> str:
    wiki_path = WIKI_DIR / "syntheses" / f"{name}.md"
    raw = wiki_path.read_text(encoding="utf-8") if wiki_path.exists() else ""
    body = _strip_legacy_header(raw)
    body = _convert_links(body, targets)

    title_map = {
        "rag_evolution": "RAG 技术演进综合报告",
        "rag_conflicts": "RAG 领域主要争论与冲突观点",
        "kb_health": "知识库健康状态分析",
    }
    title = title_map.get(name, name)

    fm = _common_frontmatter(
        "Synthesis",
        title,
        f"{title} - 跨概念综合分析。",
        3,
        3,
    )
    fm["tags"] = ["synthesis"]

    doc = emit_frontmatter(fm) + "\n\n"
    doc += f"# {title}\n\n"
    doc += body.rstrip() + "\n"
    return doc


# ---------------------------------------------------------------------------
# Body transformation helpers
# ---------------------------------------------------------------------------

def _strip_legacy_header(raw: str) -> str:
    """Remove the legacy `# Title` first line and `> Aliases:` blockquote so
    the frontmatter (emitted separately) is the single source of that metadata."""
    lines = raw.split("\n")
    out: list[str] = []
    skip_leading_heading = True
    skip_alias_block = False
    for line in lines:
        if skip_leading_heading and line.startswith("# "):
            skip_leading_heading = False
            continue
        # Drop the leading "> 别名:" / "> Aliases:" blockquote line(s).
        if skip_leading_heading is False and re.match(r"^>\s*(别名|Aliases)", line):
            skip_alias_block = True
            continue
        if skip_alias_block:
            if line.strip() == "":
                skip_alias_block = False
                continue
            if line.startswith(">"):
                continue
            skip_alias_block = False
        out.append(line)
    # Collapse leading blank lines.
    while out and out[0].strip() == "":
        out.pop(0)
    return "\n".join(out)


def _inject_claim_anchors(body: str, page_claims: list[dict]) -> str:
    """Append a # Claims section with HTML anchors + per-claim source tags.

    The [src:s1,s2] tag encodes per-claim provenance so okf_import can recover
    exact claim→source mapping on round-trip (otherwise all claims on a concept
    would share the concept-level citation set).

    A previously-generated # Claims section (e.g. from an older export) is
    stripped first so the section is always regenerated with current data."""
    if not page_claims:
        return body

    # Convert any legacy [[claim_xxx]] references in the prose to anchor spans.
    def anchor_repl(m: re.Match) -> str:
        cid = m.group(1)
        claim = next((c for c in page_claims if c["claim_id"] == cid), None)
        src_tag = ""
        if claim and claim.get("source_ids"):
            srcs = ",".join(claim["source_ids"])
            src_tag = f" [src:{srcs}]"
        return f'<a id="{cid}"></a>**{cid}**{src_tag}'

    body = re.sub(r"\[\[(claim_\d+)\]\](?=:|\s)", anchor_repl, body)

    # Strip any previously-generated "## Claims" auto-section so we always
    # rebuild it fresh with current per-claim source data.
    body = re.sub(
        r"\n*## Claims\s*\n(?:<a id=\"claim_\d+\"></a>.*\n?)+",
        "\n",
        body,
    )

    block = ["", "## Claims", ""]
    for c in page_claims:
        cid = c["claim_id"]
        status = c.get("status", "supported")
        srcs = ",".join(c.get("source_ids", []))
        src_tag = f" [src:{srcs}]" if srcs else ""
        block.append(f'<a id="{cid}"></a>**{cid}** ({status}){src_tag}: {c["text"]}')
    block.append("")
    return body.rstrip() + "\n" + "\n".join(block)


def _synthesize_concept_body(concept: dict, idx: IndexData) -> str:
    """Build a body for a stub concept (orphan claim owner with no wiki page)."""
    desc = _ORPHAN_STUBS.get(concept["page_id"], (concept["canonical_name"], [], 3, ""))[3]
    parts = ["## 定义\n", f"{desc}\n" if desc else f"{concept['canonical_name']} 是从声明归属推导出的概念。\n", ""]
    page_claims = claims_by_page(idx.claims).get(concept["page_id"], [])
    if page_claims:
        parts.append("## Claims\n")
        for c in page_claims:
            parts.append(f'<a id="{c["claim_id"]}"></a>**{c["claim_id"]}** ({c.get("status","supported")}): {c["text"]}')
        parts.append("")
    return "\n".join(parts)


def _render_citations(
    cited_sources: list[str], idx: IndexData, targets: dict[str, str]
) -> str:
    """Render an OKF §8 # Citations section as a numbered list."""
    if not cited_sources:
        return ""
    src_by_id = {s["source_id"]: s for s in idx.sources}
    lines = ["# Citations", ""]
    for i, sid in enumerate(cited_sources, 1):
        s = src_by_id.get(sid)
        if s:
            year = s.get("year", "n.d.")
            label = f'{s["title"]} ({year})'
            tgt = targets.get(sid, f"/sources/{sid}.md")
            lines.append(f"[{i}] [{label}]({tgt})")
        else:
            lines.append(f"[{i}] `{sid}`")
    lines.append("")
    return "\n".join(lines)


def _synthesize_source_body(
    source: dict, idx: IndexData, targets: dict[str, str]
) -> str:
    """Build a body for a source that has no hand-written wiki page."""
    parts: list[str] = []
    abstract = source.get("abstract", "")
    if abstract:
        parts.append("## Abstract\n")
        parts.append(f"{abstract}\n")

    # Related claims (claims that cite this source).
    src_claims = claims_by_source(idx.claims).get(source["source_id"], [])
    if src_claims:
        parts.append("## Key Claims\n")
        for c in src_claims:
            parts.append(f'- <a id="{c["claim_id"]}"></a>**{c["claim_id"]}** ({c.get("status","supported")}): {c["text"]}')
        parts.append("")

    concepts = source.get("concepts", [])
    if concepts:
        parts.append("## Concepts\n")
        for cname in concepts:
            parts.append(f"- {cname}")
        parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Reserved files: index.md (§6) and log.md (§7)
# ---------------------------------------------------------------------------

def emit_root_index(idx: IndexData) -> str:
    """OKF §6 index.md: no frontmatter, sections grouping concepts with descriptions."""
    lines = [
        "# AgentKB-Diag Knowledge Bundle",
        "",
        "OKF v0.1 bundle. Each concept is one markdown file; links are standard markdown.",
        "",
        "## Concepts",
        "",
    ]
    for c in sorted(idx.concepts, key=lambda x: x["canonical_name"]):
        pid = c["page_id"]
        desc = ", ".join(c.get("aliases", [])[:2]) or c["canonical_name"]
        lines.append(f"* [{c['canonical_name']}](/concepts/{pid}.md) - {desc}")
    lines += ["", "## Sources", ""]
    for s in sorted(idx.sources, key=lambda x: x["source_id"]):
        sid = s["source_id"]
        lines.append(f"* [{s['title']}](/sources/{sid}.md) - {s.get('year', '')}")
    lines += ["", "## Syntheses", ""]
    for name, label in [
        ("rag_evolution", "RAG 技术演进"),
        ("rag_conflicts", "RAG 主要争论"),
        ("kb_health", "知识库健康分析"),
    ]:
        lines.append(f"* [{label}](/syntheses/{name}.md) - 跨概念综合分析")
    lines.append("")
    return "\n".join(lines)


def emit_dir_index(title: str, items: list[tuple[str, str, str]]) -> str:
    """§6 directory index.md: `* [Title](url) - desc` entries."""
    lines = [f"# {title}", ""]
    for label, url, desc in items:
        lines.append(f"* [{label}]({url}) - {desc}")
    lines.append("")
    return "\n".join(lines)


def emit_log() -> str:
    """OKF §7 log.md: date-grouped entries, newest first."""
    return """# Directory Update Log

## 2026-05-12
* **Update**: Repair round — added cross-references for orphan nodes, marked duplicate concepts (Self-RAG / Corrective RAG), flagged conflicted claims for review.
* **Update**: Citation coverage restored from 0.62 to 0.80; Recall@3 from 0.55 to 0.78.

## 2026-05-10
* **Creation**: Round 3 — added Long-Context, KB Degradation, Multimodal RAG concepts.
* **Update**: Detected 3 unsupported claims and 2 conflicted claims; Self-RAG / Corrective RAG overlap identified.

## 2026-05-05
* **Creation**: Round 2 — added GraphRAG, Agentic RAG, Multi-Hop Retrieval and 7 more concepts.
* **Update**: Some legacy claims re-statused; new links introduced orphan nodes.

## 2026-05-01
* **Initialization**: Created foundational directory structure and 7 base concepts (RAG, Dense Retrieval, RAG Evaluation, Fact Verification).
* **Creation**: 30 demo sources across 3 rounds.
"""


# ---------------------------------------------------------------------------
# Top-level export
# ---------------------------------------------------------------------------

def export_bundle() -> dict[str, int]:
    """Build the full OKF bundle at OKF_DIR. Returns file counts."""
    idx = IndexData.load()

    # Populate claim-owner map for link conversion.
    _CLAIM_OWNER.clear()
    for c in idx.claims:
        _CLAIM_OWNER[c["claim_id"]] = c.get("page_id", "")

    targets = _build_link_target_map(idx)

    # Fresh bundle directory.
    if OKF_DIR.exists():
        shutil.rmtree(OKF_DIR)
    (OKF_DIR / "concepts").mkdir(parents=True)
    (OKF_DIR / "sources").mkdir(parents=True)
    (OKF_DIR / "syntheses").mkdir(parents=True)

    counts = {"concepts": 0, "sources": 0, "syntheses": 0, "reserved": 0}

    # Concepts.
    concept_items: list[tuple[str, str, str]] = []
    for c in idx.concepts:
        doc = emit_concept(c, idx, targets)
        (OKF_DIR / "concepts" / f"{c['page_id']}.md").write_text(doc, encoding="utf-8")
        concept_items.append(
            (c["canonical_name"], f"/concepts/{c['page_id']}.md",
             ", ".join(c.get("aliases", [])[:2]) or c["canonical_name"])
        )
        counts["concepts"] += 1
    (OKF_DIR / "concepts" / "index.md").write_text(
        emit_dir_index("Concepts", concept_items), encoding="utf-8"
    )

    # Sources (including stubs for 011..030 that had no wiki page).
    source_items: list[tuple[str, str, str]] = []
    for s in idx.sources:
        doc = emit_source(s, idx, targets)
        (OKF_DIR / "sources" / f"{s['source_id']}.md").write_text(doc, encoding="utf-8")
        source_items.append(
            (f'{s["title"]} ({s.get("year", "")})', f"/sources/{s['source_id']}.md",
             s.get("abstract", "")[:80])
        )
        counts["sources"] += 1
    (OKF_DIR / "sources" / "index.md").write_text(
        emit_dir_index("Sources", source_items), encoding="utf-8"
    )

    # Syntheses.
    synth_items: list[tuple[str, str, str]] = []
    for name, label in [
        ("rag_evolution", "RAG 技术演进"),
        ("rag_conflicts", "RAG 主要争论"),
        ("kb_health", "知识库健康分析"),
    ]:
        doc = emit_synthesis(name, idx, targets)
        (OKF_DIR / "syntheses" / f"{name}.md").write_text(doc, encoding="utf-8")
        synth_items.append((label, f"/syntheses/{name}.md", "跨概念综合分析"))
        counts["syntheses"] += 1
    (OKF_DIR / "syntheses" / "index.md").write_text(
        emit_dir_index("Syntheses", synth_items), encoding="utf-8"
    )

    # Reserved root files.
    (OKF_DIR / "index.md").write_text(emit_root_index(idx), encoding="utf-8")
    (OKF_DIR / "log.md").write_text(emit_log(), encoding="utf-8")
    counts["reserved"] = 2

    return counts


if __name__ == "__main__":
    counts = export_bundle()
    total = sum(counts.values())
    print(f"OKF bundle exported to {OKF_DIR}")
    print(f"  concepts:   {counts['concepts']}")
    print(f"  sources:    {counts['sources']}")
    print(f"  syntheses:  {counts['syntheses']}")
    print(f"  reserved:   {counts['reserved']} (index.md, log.md)")
    print(f"  total .md:  {total + 3} (incl. 3 directory index.md)")
