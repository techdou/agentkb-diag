"""
OKF v0.1 conformance checker.

Verifies a bundle against the OKF v0.1 spec:
  1. Every non-reserved .md file has a parseable YAML frontmatter block.
  2. Every frontmatter block contains a non-empty `type` field.
  3. Reserved filenames (index.md, log.md) follow §6/§7 structure.
  4. No [[wikilink]] residuals in concept/source/synthesis bodies.

Usage:
    python backend/scripts/okf_check.py [bundle_dir]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DEFAULT_BUNDLE = Path(__file__).resolve().parents[2] / "okf"
# Reserved filenames: §3.1 defines index.md / log.md. README.md is a bundle
# meta-document (not a concept) — treated as exempt from the frontmatter rule.
RESERVED = {"index.md", "log.md", "README.md"}
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TYPE_RE = re.compile(r"^type:\s*(\S+)", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def check_bundle(bundle: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    concept_count = 0
    source_count = 0
    synth_count = 0
    reserved_count = 0

    md_files = sorted(bundle.rglob("*.md"))
    if not md_files:
        errors.append(f"No .md files found in {bundle}")
        return _report(errors, warnings, 0, 0, 0, 0)

    for md in md_files:
        rel = md.relative_to(bundle)
        is_reserved = md.name in RESERVED
        text = md.read_text(encoding="utf-8")

        if is_reserved:
            reserved_count += 1
            # index.md: §6 — should have list items with [text](url), no frontmatter required.
            # log.md: §7 — should have ## YYYY-MM-DD headings.
            if md.name == "log.md":
                if not re.search(r"^## \d{4}-\d{2}-\d{2}", text, re.MULTILINE):
                    errors.append(f"{rel}: log.md missing ISO date headings (§7)")
            # index.md files (root and per-dir) — check they contain list links.
            if md.name == "index.md" and "](" not in text:
                warnings.append(f"{rel}: index.md has no markdown links (§6 expects listing)")
            continue

        # Non-reserved: must have frontmatter + type.
        fm = FRONTMATTER_RE.match(text)
        if not fm:
            errors.append(f"{rel}: missing YAML frontmatter block (§4.1)")
            continue
        type_match = TYPE_RE.search(fm.group(1))
        if not type_match or not type_match.group(1):
            errors.append(f"{rel}: frontmatter missing non-empty `type` field (§4.1)")
            continue
        type_val = type_match.group(1).strip("'\"")
        if type_val == "Concept":
            concept_count += 1
        elif type_val == "Source":
            source_count += 1
        elif type_val == "Synthesis":
            synth_count += 1

        # Check for wikilink residuals in body (after frontmatter).
        body = text[fm.end():]
        wl = WIKILINK_RE.findall(body)
        if wl:
            errors.append(f"{rel}: {len(wl)} [[wikilink]] residual(s): {wl[:3]}")

    # Reserved filename misuse: any non-root index.md/log.md is allowed (§3.1
    # says reserved at any level), so no extra check needed.

    return _report(errors, warnings, concept_count, source_count, synth_count, reserved_count)


def _report(
    errors: list[str],
    warnings: list[str],
    concepts: int,
    sources: int,
    syntheses: int,
    reserved: int,
) -> int:
    print("=" * 60)
    print("OKF v0.1 Conformance Report")
    print("=" * 60)
    print(f"  Concepts : {concepts}")
    print(f"  Sources  : {sources}")
    print(f"  Syntheses: {syntheses}")
    print(f"  Reserved : {reserved} (index.md / log.md)")
    print("-" * 60)
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print("-" * 60)
        print("Result: NON-CONFORMANT")
        return 1
    print("-" * 60)
    print("Result: CONFORMANT with OKF v0.1 ✓")
    return 0


if __name__ == "__main__":
    bundle = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BUNDLE
    if not bundle.exists():
        print(f"Bundle not found: {bundle}")
        sys.exit(2)
    sys.exit(check_bundle(bundle))
