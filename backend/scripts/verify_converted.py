"""Verify that each converted markdown actually matches its manifest title.

Catches "wrong arXiv id" mistakes (e.g. typo in id -> downloaded a different
paper). For each source, compares the H1 title (first `# ...` line) extracted
from the MinerU-converted markdown against the expected title in
paper_manifest.py, using token-set overlap. Flags mismatches for review.

Usage:
    python backend/scripts/verify_converted.py              # all
    python backend/scripts/verify_converted.py --round 1
    python backend/scripts/verify_converted.py --threshold 0.3
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Allow both invocation styles (see fetch_papers_by_id.py for rationale).
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from scripts.paper_manifest import get_manifest
except ImportError:
    from backend.scripts.paper_manifest import get_manifest


# Tokens to ignore when comparing titles (stopwords / generic academic words).
_STOP = {
    "a", "an", "the", "of", "for", "and", "or", "in", "on", "to", "with",
    "from", "by", "via", "through", "based", "is", "are", "using", "towards",
    "toward", "as", "its", "their", "this", "that", "these", "those",
}

# Expected converted-md filename patterns. MinerU writes source_NNN.md; the
# project convention also has source_NNN_converted.md. Accept either.
_CONVERTED_NAMES = ["source_{idx}.md", "source_{idx}_converted.md"]


def _tokens(text: str) -> set[str]:
    """Lowercase alphanumeric tokens, minus stopwords and short numerics."""
    raw = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in raw if t not in _STOP and not (t.isdigit() and len(t) < 4)}


def _extract_h1(md_text: str) -> str:
    """Return the first markdown H1 title line, stripped."""
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# ") and not s.startswith("## "):
            return s[2:].strip()
    return ""


def _overlap(expected: str, actual: str) -> tuple[float, set[str], set[str]]:
    """Token-set Jaccard-ish overlap: |shared| / |expected tokens|."""
    exp_toks = _tokens(expected)
    act_toks = _tokens(actual)
    if not exp_toks:
        return 0.0, set(), act_toks
    shared = exp_toks & act_toks
    return len(shared) / len(exp_toks), shared, exp_toks - shared


def find_converted_md(base_dir: Path, round_num: int, idx: str) -> Path | None:
    """Locate the converted md for a source, trying both naming conventions."""
    d = base_dir / "data" / "converted" / f"round_{round_num}"
    for tpl in _CONVERTED_NAMES:
        p = d / tpl.format(idx=idx)
        if p.exists():
            return p
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify converted md titles vs manifest")
    parser.add_argument("--round", type=int, choices=[1, 2, 3])
    parser.add_argument("--output-dir", default=".")
    parser.add_argument(
        "--threshold", type=float, default=0.4,
        help="Token-overlap ratio below which a paper is flagged (default 0.4)",
    )
    args = parser.parse_args()

    base_dir = Path(args.output_dir).resolve()
    manifest = get_manifest()
    if args.round:
        manifest = [m for m in manifest if m["round"] == args.round]

    print(f"{'source':<11} {'overlap':>7}  status   expected → actual title")
    print("-" * 100)
    n_ok = n_warn = n_fail = n_missing = 0
    flagged: list[tuple[str, str, float, str, str]] = []

    for entry in manifest:
        idx = entry["source_id"].split("_")[1]
        md_path = find_converted_md(base_dir, entry["round"], idx)
        if not md_path:
            print(f"{entry['source_id']:<11} {'—':>7}  MISSING  (no converted md yet)")
            n_missing += 1
            continue

        md_text = md_path.read_text(encoding="utf-8", errors="ignore")
        h1 = _extract_h1(md_text)
        ratio, shared, missing_toks = _overlap(entry["title"], h1)

        if ratio >= args.threshold:
            status = "OK"; n_ok += 1
        elif ratio >= 0.2:
            status = "WARN"; n_warn += 1
            flagged.append((entry["source_id"], entry["arxiv_id"], ratio, entry["title"], h1))
        else:
            status = "FAIL"; n_fail += 1
            flagged.append((entry["source_id"], entry["arxiv_id"], ratio, entry["title"], h1))

        h1_short = (h1[:45] + "…") if len(h1) > 46 else h1
        print(f"{entry['source_id']:<11} {ratio:>6.2f}  {status:<7}  {h1_short}")

    print("-" * 100)
    print(f"OK: {n_ok}  |  WARN: {n_warn}  |  FAIL: {n_fail}  |  MISSING: {n_missing}")

    if flagged:
        print(f"\n[FLAGGED — overlap < {args.threshold}]")
        for src, aid, r, exp, act in flagged:
            print(f"\n  {src}  arXiv:{aid}  overlap={r:.2f}")
            print(f"    expected: {exp}")
            print(f"    actual:   {act}")
        print(
            "\nA FAIL/WARN means the downloaded PDF likely does not match the intended paper "
            "(e.g. an arXiv id typo). Re-check the id and re-download."
        )
        if n_fail:
            sys.exit(1)


if __name__ == "__main__":
    main()
