"""Fetch real RAG research papers from academic APIs.

Usage:
    python -m scripts.fetch_papers --round 1 --api arxiv --max-per-query 5
    python -m scripts.fetch_papers --round 2 --api semantic_scholar
    python -m scripts.fetch_papers --round 3 --max-per-query 3

Papers are saved as Markdown files in data/raw/round_N/ with YAML frontmatter.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Search queries per round
# ---------------------------------------------------------------------------

ARXIV_SEARCHES: dict[str, list[str]] = {
    "round_1_foundations": [
        "retrieval augmented generation",
        "dense passage retrieval",
        "knowledge intensive NLP",
    ],
    "round_2_extensions": [
        "GraphRAG",
        "agentic RAG",
        "knowledge graph RAG",
        "multi hop retrieval augmented generation",
    ],
    "round_3_advanced": [
        "RAG evaluation benchmark",
        "retrieval augmented generation faithfulness",
        "long context vs RAG",
        "RAG failure modes",
    ],
}

# Round key to number mapping
ROUND_MAP: dict[int, str] = {
    1: "round_1_foundations",
    2: "round_2_extensions",
    3: "round_3_advanced",
}

# ArXiv API namespace
ARXIV_NS = "{http://www.w3.org/2005/Atom}"

# ---------------------------------------------------------------------------
# Paper model
# ---------------------------------------------------------------------------


class Paper:
    def __init__(
        self,
        title: str = "",
        authors: Optional[list[str]] = None,
        year: int = 2024,
        abstract: str = "",
        arxiv_id: str = "",
        url: str = "",
        published: str = "",
    ):
        self.title = title.strip()
        self.authors = authors or []
        self.year = year
        self.abstract = abstract.strip()
        self.arxiv_id = arxiv_id.strip()
        self.url = url.strip() or f"https://arxiv.org/abs/{self.arxiv_id}"
        self.published = published.strip()

    def to_markdown(self) -> str:
        """Render paper as a PRD-compatible source Markdown file with frontmatter."""
        authors_str = ", ".join(self.authors[:8])
        if len(self.authors) > 8:
            authors_str += " et al."

        frontmatter = f"""---
source_id: {self.arxiv_id or 'unknown'}
title: "{self.title}"
authors: [{', '.join(repr(a) for a in self.authors)}]
year: {self.year}
url: {self.url}
published: {self.published}
tags: []
---

# {self.title}

**Authors:** {authors_str}

**Year:** {self.year}

**URL:** [{self.arxiv_id}]({self.url})

## Abstract

{self.abstract}

## Full Text

*(Full text available at {self.url})*
"""
        return frontmatter


# ---------------------------------------------------------------------------
# ArXiv API
# ---------------------------------------------------------------------------

ARXIV_API = "http://export.arxiv.org/api/query"


def fetch_arxiv_papers(query: str, max_results: int = 5) -> list[Paper]:
    """Fetch papers from the arXiv API and return structured Paper objects."""
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] arXiv request failed for query '{query}': {e}", file=sys.stderr)
        return []

    root = ET.fromstring(resp.text)
    papers: list[Paper] = []

    for entry in root.findall(f"{ARXIV_NS}entry"):
        try:
            title_el = entry.find(f"{ARXIV_NS}title")
            title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else ""

            abstract_el = entry.find(f"{ARXIV_NS}summary")
            abstract = abstract_el.text.strip().replace("\n", " ") if abstract_el is not None and abstract_el.text else ""

            id_el = entry.find(f"{ARXIV_NS}id")
            arxiv_url = id_el.text.strip() if id_el is not None and id_el.text else ""
            arxiv_id = arxiv_url.rsplit("/", 1)[-1] if arxiv_url else ""
            # Strip version suffix (v1, v2, etc.)
            arxiv_id = re.sub(r"v\d+$", "", arxiv_id)

            authors: list[str] = []
            for author_el in entry.findall(f"{ARXIV_NS}author"):
                name_el = author_el.find(f"{ARXIV_NS}name")
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            published_el = entry.find(f"{ARXIV_NS}published")
            published = published_el.text.strip() if published_el is not None and published_el.text else ""
            year = int(published[:4]) if published and len(published) >= 4 else 2024

            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    arxiv_id=arxiv_id,
                    url=arxiv_url,
                    published=published,
                )
            )
        except Exception as e:
            print(f"[WARN] Skipping malformed entry: {e}", file=sys.stderr)
            continue

    return papers


# ---------------------------------------------------------------------------
# Semantic Scholar API
# ---------------------------------------------------------------------------

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"


def fetch_semantic_scholar_papers(
    query: str,
    api_key: str = "",
    max_results: int = 5,
) -> list[Paper]:
    """Fetch papers from the Semantic Scholar API."""
    headers: dict[str, str] = {"Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,authors,year,abstract,externalIds,url,publicationDate",
    }

    try:
        resp = requests.get(SEMANTIC_SCHOLAR_API, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Semantic Scholar request failed for query '{query}': {e}", file=sys.stderr)
        return []

    data = resp.json()
    papers: list[Paper] = []

    for item in data.get("data", []):
        try:
            title = item.get("title", "")
            abstract = item.get("abstract", "") or ""
            year = item.get("year") or 2024

            authors_list: list[str] = []
            for a in item.get("authors", []):
                name = a.get("name", "")
                if name:
                    authors_list.append(name)

            external_ids = item.get("externalIds", {}) or {}
            arxiv_id = external_ids.get("ArXiv", "")

            paper_url = item.get("url", "") or f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}"

            papers.append(
                Paper(
                    title=title,
                    authors=authors_list,
                    year=year,
                    abstract=abstract,
                    arxiv_id=arxiv_id,
                    url=paper_url,
                    published=item.get("publicationDate", "") or "",
                )
            )
        except Exception as e:
            print(f"[WARN] Skipping malformed S2 entry: {e}", file=sys.stderr)
            continue

    return papers


# ---------------------------------------------------------------------------
# File saving
# ---------------------------------------------------------------------------


def save_paper(paper: Paper, round_num: int, source_index: int, base_dir: Path) -> Path:
    """Save a paper as a Markdown file in data/raw/round_N/.

    Returns the path of the saved file.
    """
    out_dir = base_dir / "data" / "raw" / f"round_{round_num}"
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"source_{source_index:03d}.md"
    out_path = out_dir / filename

    content = paper.to_markdown()
    out_path.write_text(content, encoding="utf-8")
    print(f"  Saved: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch real RAG research papers from academic APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--api",
        choices=["arxiv", "semantic_scholar"],
        default="arxiv",
        help="Which academic API to query (default: arxiv)",
    )
    parser.add_argument(
        "--round",
        type=int,
        choices=[1, 2, 3],
        required=True,
        help="Which experiment round to fetch papers for (1-3)",
    )
    parser.add_argument(
        "--max-per-query",
        type=int,
        default=5,
        help="Maximum papers to fetch per search query (default: 5)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default="",
        help="API key for Semantic Scholar (optional, improves rate limits)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Project root directory where data/raw/ will be created (default: current dir)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print paper metadata without saving files",
    )

    args = parser.parse_args()

    round_key = ROUND_MAP.get(args.round, f"round_{args.round}")
    queries = ARXIV_SEARCHES.get(round_key, [])
    if not queries:
        print(f"[ERROR] No queries defined for round {args.round}", file=sys.stderr)
        sys.exit(1)

    print(f"Round {args.round} — {round_key}")
    print(f"API: {args.api}")
    print(f"Queries: {len(queries)}")
    print(f"Max per query: {args.max_per_query}")
    print()

    base_dir = Path(args.output_dir).resolve()
    all_papers: list[Paper] = []
    seen_ids: set[str] = set()

    for query in queries:
        print(f"[FETCH] {query}")
        time.sleep(0.5)  # Be respectful to the API

        if args.api == "arxiv":
            papers = fetch_arxiv_papers(query, max_results=args.max_per_query)
        else:
            papers = fetch_semantic_scholar_papers(query, api_key=args.api_key, max_results=args.max_per_query)

        # Deduplicate by arxiv_id or title
        new_count = 0
        for paper in papers:
            dedup_key = paper.arxiv_id or paper.title.lower()
            if dedup_key and dedup_key not in seen_ids:
                seen_ids.add(dedup_key)
                all_papers.append(paper)
                new_count += 1

        print(f"  Retrieved {len(papers)} papers, {new_count} new (unique)")
        print()

    print(f"Total unique papers: {len(all_papers)}")

    if args.dry_run:
        print("\n[Dry run] Paper metadata:\n")
        for i, paper in enumerate(all_papers):
            authors_short = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_short += " et al."
            print(f"  {i + 1}. {paper.title}")
            print(f"     Authors: {authors_short}")
            print(f"     Year: {paper.year}")
            print(f"     ID: {paper.arxiv_id}")
            print(f"     Abstract: {paper.abstract[:200]}...")
            print()
        return

    for i, paper in enumerate(all_papers):
        save_paper(paper, args.round, i + 1, base_dir)

    print(f"\nDone. Saved {len(all_papers)} papers to data/raw/round_{args.round}/")

    # Print a summary JSON that can be used as an index
    summary = [
        {
            "source_id": p.arxiv_id or f"SRC-{args.round:03d}-{i + 1:03d}",
            "title": p.title,
            "authors": p.authors,
            "year": p.year,
            "url": p.url,
        }
        for i, p in enumerate(all_papers)
    ]
    summary_path = base_dir / "data" / "raw" / f"round_{args.round}" / "_index.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Index written to {summary_path}")


if __name__ == "__main__":
    main()
