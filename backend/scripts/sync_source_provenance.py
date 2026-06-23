"""Append dataset-mapping provenance to OKF source files for replace/approx papers.

For each source whose manifest entry is mapping=="replace" or "approx", append a
provenance block to okf/sources/source_NNN.md recording the actual arXiv id and
title used (since the original stub was fabricated or only approximated).

Idempotent: uses a HTML-comment marker so re-running won't duplicate the block.
Preserves the existing frontmatter, claim/concept links, and body untouched.

Usage:
    python backend/scripts/sync_source_provenance.py           # apply
    python backend/scripts/sync_source_provenance.py --dry-run  # preview
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from scripts.paper_manifest import get_manifest
except ImportError:
    from backend.scripts.paper_manifest import get_manifest

MARKER_START = "<!-- DATASET_MAPPING_PROVENANCE -->"
MARKER_END = "<!-- /DATASET_MAPPING_PROVENANCE -->"


def build_block(entry: dict) -> str:
    """Build the provenance markdown block for one source."""
    aid = entry["arxiv_id"]
    lines = [
        "",
        MARKER_START,
        "",
        "## 数据集映射说明（Dataset Mapping Provenance）",
        "",
        f"> 本 slot 在实验数据集中实际采用的论文（原始 source 预告的论文为虚构或仅近似）。",
        "",
        f"- **实际论文**: {entry['title']}",
        f"- **arXiv ID**: [`{aid}`](https://arxiv.org/abs/{aid})",
        f"- **映射类型**: `{entry['mapping']}`",
        f"- **所在轮次**: round_{entry['round']}",
    ]
    note = entry.get("note")
    if note:
        lines.append(f"- **说明**: {note}")
    lines += ["", f"完整转换文本见 `data/converted/round_{entry['round']}/source_{entry['source_id'].split('_')[1]}.md`（MinerU 从 PDF 解析）。", "", MARKER_END, ""]
    return "\n".join(lines)


def strip_existing_block(content: str) -> str:
    """Remove any previously inserted block (so re-running is idempotent)."""
    if MARKER_START not in content:
        return content
    start = content.index(MARKER_START)
    end = content.find(MARKER_END)
    if end == -1:
        # Malformed (no end marker) — remove from start to EOF
        return content[:start].rstrip() + "\n"
    return (content[:start].rstrip() + "\n" + content[end + len(MARKER_END):]).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync dataset-mapping provenance to OKF sources")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    args = parser.parse_args()

    okf_sources = _PROJECT_ROOT / "okf" / "sources"
    manifest = get_manifest()

    targets = [m for m in manifest if m["mapping"] in ("replace", "approx")]
    updated = 0
    skipped_missing = 0
    unchanged = 0

    for entry in targets:
        idx = entry["source_id"].split("_")[1]
        path = okf_sources / f"source_{idx}.md"
        if not path.exists():
            print(f"  [SKIP] {entry['source_id']}: {path.name} not found")
            skipped_missing += 1
            continue

        original = path.read_text(encoding="utf-8")
        cleaned = strip_existing_block(original)
        new_block = build_block(entry)
        new_content = cleaned.rstrip() + "\n" + new_block

        if new_content == original:
            unchanged += 1
            continue

        if args.dry_run:
            print(f"  [DRY] {entry['source_id']}: would append provenance (arXiv:{entry['arxiv_id']})")
        else:
            path.write_text(new_content, encoding="utf-8")
            print(f"  [OK]   {entry['source_id']}: provenance synced (arXiv:{entry['arxiv_id']})")
        updated += 1

    print(f"\nTargets: {len(targets)}  |  Updated: {updated}  |  Unchanged: {unchanged}  |  Missing: {skipped_missing}")


if __name__ == "__main__":
    main()
