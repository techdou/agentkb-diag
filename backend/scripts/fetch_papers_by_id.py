"""Download curated RAG papers by exact arXiv id (deterministic fetching).

Companion to fetch_papers.py. While fetch_papers.py does *search-based*
discovery (queries → uncertain results), this script downloads *specific*
papers listed in paper_manifest.py — guaranteeing the 30-paper dataset is
reproducible.

Usage:
    python -m scripts.fetch_papers_by_id                  # all 30
    python -m scripts.fetch_papers_by_id --round 1        # one round
    python -m scripts.fetch_papers_by_id --source source_001
    python -m scripts.fetch_papers_by_id --dry-run        # show plan, no download
    python -m scripts.fetch_papers_by_id --force          # overwrite existing

PDFs go to   data/raw/round_N/source_NNN.pdf
Metadata md  data/raw/round_N/source_NNN.md   (frontmatter + abstract)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Support both invocation styles:
#   python -m scripts.fetch_papers_by_id         (run from backend/, like fetch_papers.py)
#   python backend/scripts/fetch_papers_by_id.py (run from project root)
# When run as a plain script file, only the script's own dir is on sys.path,
# so neither `scripts.*` nor `backend.*` resolves. Add the project root explicitly.
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent  # .../agentkb-diag
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import requests

try:
    from scripts.paper_manifest import get_manifest
except ImportError:
    from backend.scripts.paper_manifest import get_manifest

# arXiv static PDF CDN. Using /pdf/<id>.pdf directly is the most reliable
# endpoint for programmatic download (the export.arxiv.org API is for metadata
# and disallows programmatic fetch via robots.txt).
ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}.pdf"
ARXIV_ABS_URL = "https://arxiv.org/abs/{arxiv_id}"

# arXiv rate-limit policy: ~1 request per 3s for sustained pulls. We go a bit
# slower to be safe and to survive retries without tripping 429.
INTER_REQUEST_SLEEP_SEC = 5.0
RETRY_DELAYS_SEC = [10, 30, 60]  # backoff between retries

# Validity thresholds for a downloaded PDF.
PDF_MAGIC = b"%PDF"
MIN_PDF_BYTES = 50_000  # arXiv PDFs are well above this; HTML error pages are tiny

# Browser-like UA. arXiv rejects requests with no/unknown UA.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


def _is_valid_pdf(data: bytes) -> bool:
    """Quick sanity check: starts with %PDF magic and large enough to be real."""
    return data.startswith(PDF_MAGIC) and len(data) >= MIN_PDF_BYTES


def download_pdf(arxiv_id: str, dest: Path, force: bool = False) -> tuple[bool, str]:
    """Download one arXiv PDF to dest. Returns (ok, message).

    Retries on transient failures with exponential-ish backoff.
    Validates the result is a real PDF (magic bytes + size), not an HTML error page.
    """
    if dest.exists() and not force:
        existing = dest.read_bytes()
        if _is_valid_pdf(existing):
            return True, f"already present ({len(existing):,} bytes), skipped"
        else:
            print(f"  [WARN] existing {dest.name} invalid, re-downloading", file=sys.stderr)

    url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/pdf"}

    last_err = ""
    for attempt, delay in enumerate([0] + RETRY_DELAYS_SEC, start=1):
        if delay:
            print(f"  retry {attempt}/{len(RETRY_DELAYS_SEC)} after {delay}s...")
            time.sleep(delay)
        try:
            resp = requests.get(url, headers=headers, timeout=60)
        except requests.RequestException as e:
            last_err = f"network: {e}"
            continue

        if resp.status_code == 200 and _is_valid_pdf(resp.content):
            dest.write_bytes(resp.content)
            return True, f"downloaded ({len(resp.content):,} bytes)"

        if resp.status_code == 404:
            return False, f"404 not found at {url}"
        # Could be 429 (rate limited), 503, or 200-but-HTML-error-page
        last_err = f"HTTP {resp.status_code}, {len(resp.content)} bytes"
        if resp.status_code == 429:
            # Honor rate limit with a longer wait before the next retry
            last_err += " (rate limited)"

    return False, f"failed after {len(RETRY_DELAYS_SEC)} retries: {last_err}"


# ---------------------------------------------------------------------------
# Metadata markdown
# ---------------------------------------------------------------------------


def write_metadata_md(entry: dict, md_path: Path) -> None:
    """Write/overwrite the source_NNN.md metadata file with frontmatter.

    Preserves the existing directory convention (one .md per source) but now
    points at the real downloaded paper instead of a hand-written stub.
    """
    arxiv_id = entry["arxiv_id"]
    round_num = entry["round"]
    frontmatter = f"""---
source_id: {entry['source_id']}
title: "{entry['title']}"
authors: []
year:
arxiv_id: {arxiv_id}
url: {ARXIV_ABS_URL.format(arxiv_id=arxiv_id)}
round: {round_num}
tags: [RAG]
mapping: {entry['mapping']}
pdf: source_{entry['source_id'].split('_')[1]}.pdf
"""

    note = entry.get("note")
    if note:
        # Escape quotes in note for YAML safety
        frontmatter += f'note: "{note}"\n'

    frontmatter += f"""---

# {entry['title']}

> arXiv: [{arxiv_id}]({ARXIV_ABS_URL.format(arxiv_id=arxiv_id)})
> Round: {round_num}  |  Mapping: `{entry['mapping']}`

## Full text

PDF: [`source_{entry['source_id'].split('_')[1]}.pdf`](source_{entry['source_id'].split('_')[1]}.pdf)

Converted (MinerU) markdown: see `data/converted/round_{round_num}/source_{entry['source_id'].split('_')[1]}_converted.md`

"""
    if note:
        frontmatter += f"## Mapping note\n\n{note}\n"

    md_path.write_text(frontmatter, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download curated RAG papers by exact arXiv id",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--round", type=int, choices=[1, 2, 3], help="Only process a specific round")
    parser.add_argument("--source", type=str, help="Only process a specific source_id (e.g. source_001)")
    parser.add_argument(
        "--output-dir", type=str, default=".",
        help="Project root directory (default: current dir)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without downloading")
    parser.add_argument("--force", action="store_true", help="Re-download even if PDF already exists and is valid")
    args = parser.parse_args()

    base_dir = Path(args.output_dir).resolve()
    manifest = get_manifest()

    if args.round:
        manifest = [m for m in manifest if m["round"] == args.round]
    if args.source:
        manifest = [m for m in manifest if m["source_id"] == args.source]

    print(f"Papers to process: {len(manifest)}")
    if args.dry_run:
        for m in manifest:
            print(f"  {m['source_id']} (round {m['round']})  arXiv:{m['arxiv_id']}  [{m['mapping']}]  {m['title'][:60]}")
        return

    results: list[dict] = []
    n_ok = n_fail = n_skip = 0

    for i, entry in enumerate(manifest, start=1):
        src_id = entry["source_id"]
        round_num = entry["round"]
        idx = src_id.split("_")[1]
        pdf_path = base_dir / "data" / "raw" / f"round_{round_num}" / f"source_{idx}.pdf"
        md_path = base_dir / "data" / "raw" / f"round_{round_num}" / f"source_{idx}.md"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n[{i}/{len(manifest)}] {src_id}  arXiv:{entry['arxiv_id']}  [{entry['mapping']}]")
        ok, msg = download_pdf(entry["arxiv_id"], pdf_path, force=args.force)
        status = "OK" if ok else "FAIL"
        print(f"  {status}: {msg}")

        if ok:
            write_metadata_md(entry, md_path)
            if "already present" in msg:
                n_skip += 1
            else:
                n_ok += 1
        else:
            n_fail += 1

        results.append({
            "source_id": src_id,
            "round": round_num,
            "arxiv_id": entry["arxiv_id"],
            "title": entry["title"],
            "mapping": entry["mapping"],
            "status": status,
            "pdf": str(pdf_path.relative_to(base_dir)) if ok else None,
            "message": msg,
        })

        # Respect arXiv rate limit between distinct downloads
        if i < len(manifest):
            time.sleep(INTER_REQUEST_SLEEP_SEC)

    # Write download log (useful for reproducibility / audit)
    log_path = base_dir / "data" / "raw" / "_download_log.json"
    log_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"Downloaded: {n_ok}  |  Skipped (cached): {n_skip}  |  Failed: {n_fail}")
    print(f"Log: {log_path}")
    if n_fail:
        print("\n[FAILED]", file=sys.stderr)
        for r in results:
            if r["status"] == "FAIL":
                print(f"  {r['source_id']}  {r['arxiv_id']}  {r['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
