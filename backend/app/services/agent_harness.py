"""
Agent Harness — clean orchestration framework for the LLM Agent Pipeline.

The pipeline has 7 agent roles executed sequentially:
  Ingest → Summary → Concept Extraction → Claim Extraction →
  Wiki Writer → Link Builder → Update Agent

Two execution modes:
  - "rule":  regex + template-based extraction (no API key required)
  - "llm":   calls OpenAI-compatible or Anthropic API for structured output
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import httpx

from app.services.agent_logger import AgentLogger

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class AgentMode(Enum):
    RULE = "rule"
    LLM = "llm"


class AgentRole(Enum):
    INGEST = "ingest"
    SUMMARY = "summary"
    CONCEPT = "concept"
    CLAIM = "claim"
    WIKI_WRITER = "wiki_writer"
    LINK_BUILDER = "link_builder"
    UPDATE = "update"


@dataclass
class AgentConfig:
    """Configuration for the agent harness."""

    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 2048
    mode: AgentMode = AgentMode.RULE
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class SourceInfo:
    """Structured representation of a source document."""

    source_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int = 2024
    abstract: str = ""
    full_text: str = ""
    round_num: int = 1
    tags: list[str] = field(default_factory=list)


@dataclass
class ExtractedConcept:
    """A concept extracted from source text."""

    canonical_name: str
    aliases: list[str] = field(default_factory=list)
    definition: str = ""
    frequency: int = 1


@dataclass
class ExtractedClaim:
    """A knowledge claim with provenance."""

    claim_id: str
    text: str
    source_ids: list[str] = field(default_factory=list)
    confidence: float = 1.0
    status: str = "supported"


@dataclass
class WikiPage:
    """Generated Markdown wiki page (OKF v0.1 compliant).

    `content` carries the full markdown body *including* the YAML frontmatter
    block, so it can be written verbatim to the bundle. `frontmatter` is the
    parsed dict for programmatic access; emitters keep the two in sync.
    """

    page_id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    page_type: str = "concept"  # concept | source | synthesis
    round_num: int = 1
    frontmatter: dict = field(default_factory=dict)


@dataclass
class ExtractedLink:
    """A relationship between two pages, expressed as a standard markdown link."""

    source_page_id: str
    target_page_id: str
    link_type: str = "references"  # references | extends | uses | related
    confidence: float = 1.0
    context: str = ""


@dataclass
class PipelineResult:
    """Result of running the full agent pipeline."""

    round_num: int
    mode: str
    sources: list[SourceInfo] = field(default_factory=list)
    summaries: dict[str, str] = field(default_factory=dict)  # source_id → summary
    concepts: list[ExtractedConcept] = field(default_factory=list)
    claims: list[ExtractedClaim] = field(default_factory=list)
    wiki_pages: list[WikiPage] = field(default_factory=list)
    links: list[ExtractedLink] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent role system prompts (LLM mode)
# ---------------------------------------------------------------------------

SYSTEM_PROMPTS: dict[AgentRole, str] = {
    AgentRole.INGEST: textwrap.dedent("""\
        You are an Ingest Agent for a research knowledge base.
        Parse the provided text and extract structured bibliographic metadata.
        Return a JSON object with keys: title, authors (list), year (int),
        abstract (string), tags (list of strings).
        If any field cannot be determined, use reasonable defaults or empty lists.
        Always output valid JSON only, no commentary."""),
    AgentRole.SUMMARY: textwrap.dedent("""\
        You are a Summary Agent for a research knowledge base.
        Generate a concise summary (180-220 words) in Chinese of the provided text.
        Focus on: (1) the main research question, (2) the key method or approach,
        (3) the primary findings or contributions.
        Return a JSON object with key: summary (string).
        Always output valid JSON only, no commentary."""),
    AgentRole.CONCEPT: textwrap.dedent("""\
        You are a Concept Extraction Agent for a retrieval-augmented generation
        (RAG) research knowledge base. Extract 3-6 RAG-specific concepts from the
        provided text. For each concept provide:
          - canonical_name: normalized concept name (e.g. "GraphRAG")
          - aliases: list of alternative names or abbreviations
          - definition: concise one-sentence definition
        Return JSON: {"concepts": [{"canonical_name":..., "aliases":..., "definition":...}]}
        Always output valid JSON only, no commentary."""),
    AgentRole.CLAIM: textwrap.dedent("""\
        You are a Claim Extraction Agent for a research knowledge base.
        Extract 3-5 verifiable knowledge claims from the provided text.
        Each claim should be a single, self-contained declarative statement
        that can be supported or refuted by evidence.
        Return JSON: {"claims": [{"text":..., "confidence": 0.0-1.0}]}
        Always output valid JSON only, no commentary."""),
    AgentRole.WIKI_WRITER: textwrap.dedent("""\
        You are a Wiki Writer Agent producing OKF v0.1 (Open Knowledge Format)
        documents. Each page MUST begin with a YAML frontmatter block:
        ---
        type: Concept            # or Source / Synthesis
        title: <display name>
        description: <one-line summary>
        tags: [<tag>, ...]
        timestamp: <ISO 8601>
        ---
        Followed by a markdown body. Use STANDARD markdown links
        [text](/concepts/Page.md) to relate concepts — never [[wikilinks]].
        Sections: ## Overview, ## Claims, # Citations (numbered, for sources).
        Return JSON: {"pages": [{"title":..., "frontmatter":..., "content":...}]}
        Always output valid JSON only, no commentary."""),
    AgentRole.LINK_BUILDER: textwrap.dedent("""\
        You are a Link Builder Agent for an OKF v0.1 knowledge bundle.
        Analyze the provided concept documents and detect relationships,
        expressing each as a STANDARD markdown link [text](/concepts/Page.md)
        in the source document body. Never use [[wikilink]] syntax.
        Link types: references, extends, uses, related.
        Return JSON: {"links": [{"source":..., "target":..., "type":..., "confidence":...}]}
        Always output valid JSON only, no commentary."""),
    AgentRole.UPDATE: textwrap.dedent("""\
        You are an Update Agent for a multi-round wiki knowledge base.
        Given existing wiki pages and new source information, detect:
        (1) pages that need updating, (2) new pages to create,
        (3) pages that may be obsolete.
        Return JSON: {"updates": [{"page_id":..., "action": "update|create|archive", "reason":...}]}
        Always output valid JSON only, no commentary."""),
}

# ---------------------------------------------------------------------------
# Rule-mode extractors
# ---------------------------------------------------------------------------

# RAG-specific concept patterns used by rule extraction
RAG_CONCEPT_PATTERNS: list[tuple[str, str]] = [
    # (regex pattern, canonical name)
    (r"RAG|Retrieval[-\s]?Augmented\s*Generation|检索增强生成", "RAG"),
    (r"GraphRAG|Graph[-\s]?RAG|图增强.*生成", "GraphRAG"),
    (r"Agentic\s*RAG|Agent[-\s]?RAG|智能体RAG|Agentic\s*Retrieval", "Agentic_RAG"),
    (r"Dense\s*(Passage\s*)?Retrieval|DPR|稠密检索|Dense\s*Retrieval", "Dense_Retrieval"),
    (r"KG[-\s]?RAG|Knowledge\s*Graph.*RAG|知识图谱.*RAG", "KG_RAG"),
    (r"Multi[-\s]?Hop\s*(Retrieval|RAG)|多跳检索", "Multi_Hop_Retrieval"),
    (r"Self[-\s]?RAG|Self[-\s]?Reflective\s*RAG", "Self_RAG"),
    (r"Corrective\s*RAG|CRAG|校正.*RAG", "Corrective_RAG"),
    (r"RAG\s*Evaluation|RAG.*Benchmark|RAGAS|检索评估", "RAG_Evaluation"),
    (r"Citation\s*Faithfulness|引用.*忠实度|Citation\s*Quality", "Citation_Faithfulness"),
    (r"Long[-\s]?Context|Long[-\s]?Context.*LLM|长上下文", "Long_Context"),
    (r"Multimodal\s*RAG|多模态.*RAG|Vision.*RAG", "Multimodal_RAG"),
    (r"HyDE|Hypothetical\s*Document\s*Embedding", "HyDE"),
    (r"ReAct|Reasoning\s*and?\s*Acting", "ReAct"),
    (r"Knowledge\s*Base\s*Degradation|KB\s*Degradation|知识库退化", "KB_Degradation"),
]

# Claim extraction patterns — matches sentences that make a knowledge claim
CLAIM_PATTERNS: list[tuple[str, str]] = [
    # (regex, claim template label)
    (r"(improves?|outperforms?|achieves?).*?(by|up to)\s*(\d+(?:\.\d+)?\s*%?)", "performance_claim"),
    (r"(we\s+propose|we\s+introduce|we\s+present|this\s+paper\s+introduces?)", "method_claim"),
    (r"(results?\s+(show|demonstrate|indicate|suggest|reveal))", "finding_claim"),
    (r"(state[-\s]?of[-\s]?the[-\s]?art|SOTA|best.*result)", "sota_claim"),
    (r"(limitation|drawback|challenge|problem|issue).*?(is|are|remains)", "limitation_claim"),
]


def _rule_extract_bibliographic(text: str) -> dict[str, Any]:
    """Extract bibliographic metadata using regex heuristics."""
    lines = text.strip().splitlines()
    title = ""
    authors: list[str] = []
    year = 2024
    abstract = ""

    # Title: first non-empty line that looks like a title (not starting with abstract/keywords)
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        low = stripped.lower()
        if not any(
            low.startswith(w)
            for w in ["abstract", "keywords", "http", "doi", "introduction", "figure"]
        ):
            title = stripped[:200]
            break

    # Authors: look for author-like lines (comma-separated names, et al.)
    author_pattern = re.compile(
        r"([A-Z][a-z]+(?:\s+[A-Z]\.?)*\s*(?:,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)*)*)",
        re.UNICODE,
    )
    for line in lines[:15]:
        m = author_pattern.search(line)
        if m and len(m.group(1)) > 10 and "," in line:
            authors = [a.strip() for a in line.split(",") if a.strip()]
            break
    if not authors:
        for line in lines[:15]:
            m = re.search(r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+\s+[A-Z][a-z]+)?)", line)
            if m:
                authors = [m.group(1)]
                break

    # Year: 4-digit number between 2018-2026
    for line in lines[:20]:
        m = re.search(r"\b(20(?:1[89]|2[0-6]))\b", line)
        if m:
            year = int(m.group(1))
            break

    # Abstract: block after "Abstract" heading
    in_abstract = False
    abstract_lines: list[str] = []
    for line in lines:
        if re.match(r"^Abstract[\s\-:]*$", line, re.IGNORECASE):
            in_abstract = True
            continue
        if in_abstract and re.match(r"^(1\.?\s|Introduction|Keywords)", line, re.IGNORECASE):
            break
        if in_abstract and line.strip():
            abstract_lines.append(line.strip())
    abstract = " ".join(abstract_lines[:10]) if abstract_lines else text[:500]

    # Tags
    tags: list[str] = []
    tag_keywords = [
        ("RAG", ["RAG", "retrieval augmented generation", "检索增强"]),
        ("GraphRAG", ["GraphRAG", "graph", "knowledge graph"]),
        ("Agentic", ["agentic", "agent", "智能体"]),
        ("Evaluation", ["evaluation", "benchmark", "评估"]),
        ("MultiHop", ["multi-hop", "multi hop", "多跳"]),
    ]
    text_lower = text.lower()
    for tag, keywords in tag_keywords:
        if any(kw.lower() in text_lower for kw in keywords):
            tags.append(tag)

    return {"title": title, "authors": authors, "year": year, "abstract": abstract, "tags": tags}


def _rule_generate_summary(text: str) -> str:
    """Generate a Chinese summary using heuristic extraction."""
    sentences = re.split(r"(?<=[。；.!?])\s*", text)
    key_sentences: list[str] = []
    keywords_map = {
        "propose": "提出",
        "introduce": "引入",
        "method": "方法",
        "result": "结果",
        "experiment": "实验",
        "evaluation": "评估",
        "outperform": "优于",
        "improve": "提升",
        "limitation": "局限",
        "RAG": "检索增强生成(RAG)",
        "GraphRAG": "图增强检索(GraphRAG)",
        "retrieval": "检索",
        "generation": "生成",
    }
    for sentence in sentences:
        s = sentence.strip()
        if len(s) < 20 or len(s) > 400:
            continue
        score = sum(1 for kw in keywords_map if kw.lower() in s.lower())
        if score >= 1:
            key_sentences.append(s)
        if len(key_sentences) >= 8:
            break

    if len(key_sentences) < 2:
        # Fallback: use first 3 substantial sentences
        key_sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 400][:4]

    combined = "。".join(key_sentences[:6]) + "。"
    # Truncate to roughly 200 words (Chinese characters)
    if len(combined) > 500:
        combined = combined[:500] + "。"
    return combined


def _rule_extract_concepts(text: str) -> list[ExtractedConcept]:
    """Extract RAG concepts by pattern matching on terminology."""
    found: dict[str, ExtractedConcept] = {}
    text_lower = text.lower()

    for pattern, canonical in RAG_CONCEPT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Build a definition from context around the first match
            first_match = re.search(pattern, text, re.IGNORECASE)
            ctx_start = max(0, (first_match.start() if first_match else 0) - 50)
            ctx_end = min(len(text), (first_match.end() if first_match else 50) + 150)
            context_snippet = text[ctx_start:ctx_end].strip()
            definition = context_snippet[:200].replace("\n", " ") if context_snippet else ""

            if canonical not in found:
                found[canonical] = ExtractedConcept(
                    canonical_name=canonical,
                    aliases=[],
                    definition=definition,
                    frequency=len(matches),
                )
            else:
                found[canonical].frequency += len(matches)

    # Sort by frequency descending, take top 6
    concepts = sorted(found.values(), key=lambda c: c.frequency, reverse=True)[:6]
    # Ensure at least 3
    return concepts if len(concepts) >= 3 else concepts


def _rule_extract_claims(text: str, source_id: str) -> list[ExtractedClaim]:
    """Extract knowledge claims using sentence-level heuristics."""
    sentences = re.split(r"(?<=[.!?;])\s+", text)
    claims: list[ExtractedClaim] = []
    claim_idx = 0

    for sentence in sentences:
        s = sentence.strip()
        if len(s) < 30 or len(s) > 300:
            continue

        matched_type: Optional[str] = None
        for pattern, claim_type in CLAIM_PATTERNS:
            if re.search(pattern, s, re.IGNORECASE):
                matched_type = claim_type
                break

        if matched_type:
            prefix = source_id.split("_")[-1] if "_" in source_id else source_id
            claims.append(
                ExtractedClaim(
                    claim_id=f"CLM-{prefix}-{claim_idx:03d}",
                    text=s[:250],
                    source_ids=[source_id],
                    confidence=0.8,
                )
            )
            claim_idx += 1

        if len(claims) >= 5:
            break

    # If we didn't find enough claims, grab any substantial declarative sentences
    if len(claims) < 2:
        for sentence in sentences:
            s = sentence.strip()
            if 30 < len(s) < 300 and s not in [c.text for c in claims]:
                claims.append(
                    ExtractedClaim(
                        claim_id=f"CLM-{source_id}-{claim_idx:03d}",
                        text=s[:250],
                        source_ids=[source_id],
                        confidence=0.6,
                    )
                )
                claim_idx += 1
                if len(claims) >= 4:
                    break

    return claims


def _slugify(text: str) -> str:
    """Convert text to a safe page-id slug."""
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", s)
    s = s.strip("_")
    return s or "unnamed"


def _emit_okf_frontmatter(fields: dict) -> str:
    """Emit a minimal YAML frontmatter block (OKF v0.1). Only `type` is
    required by the spec; we always include the recommended fields too."""
    lines = ["---"]
    for key in ("type", "title", "description", "tags", "timestamp",
                "round_created", "round_updated", "aliases", "okf_version"):
        if key not in fields:
            continue
        val = fields[key]
        if isinstance(val, list):
            inner = ", ".join(str(v) for v in val)
            lines.append(f"{key}: [{inner}]")
        elif isinstance(val, (int, float)):
            lines.append(f"{key}: {val}")
        elif val == "" or val is None:
            lines.append(f'{key}: ""')
        elif key == "type":
            # type is a bare scalar per OKF spec (required, unquoted).
            lines.append(f"{key}: {val}")
        else:
            lines.append(f'{key}: "{val}"')
    lines.append("---")
    return "\n".join(lines)


def _rule_generate_wiki_pages(
    sources: list[SourceInfo],
    concepts: list[ExtractedConcept],
    claims: list[ExtractedClaim],
    round_num: int,
) -> list[WikiPage]:
    """Generate OKF v0.1 Markdown pages from extracted data.

    Each page carries a YAML frontmatter block + a markdown body that uses
    standard markdown links (no [[wikilink]])."""
    pages: list[WikiPage] = []
    okf_ts = f"2026-05-{1 + (round_num - 1) * 4:02d}T10:00:00Z"

    # Source pages — one per source.
    for src in sources:
        body_parts = [f"# {src.title}\n"]
        if src.authors:
            body_parts.append(f"> {', '.join(src.authors)} ({src.year})\n")
        body_parts.append(f"\n## Abstract\n\n{src.abstract}\n")
        src_claims = [c for c in claims if c.source_ids and src.source_id in c.source_ids]
        if src_claims:
            body_parts.append("\n## Key Claims\n")
            for c in src_claims:
                body_parts.append(f"- **{c.claim_id}** ({c.status}): {c.text}")
            body_parts.append("")

        fm = {
            "type": "Source",
            "title": src.title,
            "description": (src.abstract[:120] + "…") if len(src.abstract) > 120 else src.abstract,
            "tags": src.tags,
            "timestamp": okf_ts,
            "round_created": round_num,
            "round_updated": round_num,
            "okf_version": "0.1",
        }
        content = _emit_okf_frontmatter(fm) + "\n\n" + "".join(body_parts)
        pages.append(
            WikiPage(
                page_id=f"source_{src.source_id}",
                title=src.title,
                content=content,
                tags=src.tags,
                page_type="source",
                round_num=round_num,
                frontmatter=fm,
            )
        )

    # Concept pages — one per extracted concept.
    for concept in concepts:
        cid = _slugify(concept.canonical_name)
        body_parts = [f"# {concept.canonical_name}\n"]
        if concept.definition:
            body_parts.append(f"\n## Overview\n\n{concept.definition}\n")
        # Claims belonging to this concept (match by text overlap is crude in
        # rule mode; attach all claims whose source mentions the concept).
        concept_claims = [
            c for c in claims
            if concept.canonical_name.lower() in c.text.lower()
        ]
        if concept_claims:
            body_parts.append("\n## Claims\n")
            for c in concept_claims:
                body_parts.append(
                    f'- <a id="{c.claim_id}"></a>**{c.claim_id}** ({c.status}): {c.text}'
                )
            body_parts.append("")

        if concept.aliases:
            body_parts.append("\n## Aliases\n")
            for alias in concept.aliases[:5]:
                body_parts.append(f"- {alias}")
            body_parts.append("")

        # Standard markdown links to sources that discuss this concept.
        related_sources = [
            s for s in sources
            if concept.canonical_name.replace("_", " ").lower() in s.full_text.lower()
        ]
        if related_sources:
            body_parts.append("\n## Related Sources\n")
            for s in related_sources[:5]:
                body_parts.append(
                    f"- [{s.title}](/sources/source_{s.source_id}.md)"
                )
            body_parts.append("")

        fm = {
            "type": "Concept",
            "title": concept.canonical_name,
            "description": (concept.definition[:120] + "…") if concept.definition and len(concept.definition) > 120 else (concept.definition or concept.canonical_name),
            "tags": [concept.canonical_name.lower().replace(" ", "-")],
            "timestamp": okf_ts,
            "round_created": round_num,
            "round_updated": round_num,
            "aliases": concept.aliases,
            "okf_version": "0.1",
        }
        content = _emit_okf_frontmatter(fm) + "\n\n" + "".join(body_parts)
        pages.append(
            WikiPage(
                page_id=f"concept_{cid}",
                title=concept.canonical_name,
                content=content,
                tags=[concept.canonical_name],
                page_type="concept",
                round_num=round_num,
                frontmatter=fm,
            )
        )

    return pages


def _rule_detect_links(pages: list[WikiPage], concepts: list[ExtractedConcept]) -> list[ExtractedLink]:
    """Detect links between pages based on token-level concept mention.

    Uses the shared tokenizer (ASCII words + CJK bigrams) so that "RAG" no
    longer matches "GraphRAG" as a substring — matching is done against the
    set of tokens in the source page's content."""
    from app.core.tokenize import tokenize as _tok

    links: list[ExtractedLink] = []

    # Build a canonical-name -> page_id index, plus an alias -> canonical map,
    # so a page is detected when any of its names/aliases appears as a token.
    name_to_page: dict[str, str] = {}
    alias_targets: list[tuple[str, str]] = []  # (lowercased alias, page_id)
    page_by_id = {p.page_id: p for p in pages}
    for concept in concepts:
        pid = f"concept_{_slugify(concept.canonical_name)}"
        if pid in page_by_id:
            name_to_page[concept.canonical_name.lower()] = pid
            alias_targets.append((concept.canonical_name.lower(), pid))
            for alias in concept.aliases:
                alias_targets.append((alias.lower(), pid))

    for page_a in pages:
        content_tokens = set(_tok(page_a.content))
        matched_pages: set[str] = set()
        for alias_lower, target_pid in alias_targets:
            if target_pid == page_a.page_id:
                continue
            # Match ASCII tokens directly; for multi-token aliases, require all
            # their tokens present; for CJK, the alias must itself be a token.
            alias_tokens = set(_tok(alias_lower))
            if alias_tokens and alias_tokens.issubset(content_tokens):
                matched_pages.add(target_pid)

        for target_pid in matched_pages:
            content_lower = page_a.content.lower()
            link_type = "references"
            if "extend" in content_lower or "基于" in content_lower:
                link_type = "extends"
            elif "use" in content_lower or "使用" in content_lower:
                link_type = "uses"
            links.append(ExtractedLink(
                source_page_id=page_a.page_id,
                target_page_id=target_pid,
                link_type=link_type,
                confidence=0.7,
            ))

    # Deduplicate
    seen: set[tuple[str, str]] = set()
    deduped: list[ExtractedLink] = []
    for link in links:
        key = (link.source_page_id, link.target_page_id)
        if key not in seen:
            seen.add(key)
            deduped.append(link)

    return deduped[:100]  # Cap to prevent explosion


# ---------------------------------------------------------------------------
# LLM mode helpers
# ---------------------------------------------------------------------------

async def _call_llm(
    config: AgentConfig,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Call the configured LLM API with retry logic. Returns raw response text."""
    headers: dict[str, str] = {"Content-Type": "application/json"}
    payload: dict[str, Any] = {
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    if config.provider in ("openai", "ollama"):
        base_url = "https://api.openai.com/v1" if config.provider == "openai" else "http://localhost:11434/v1"
        headers["Authorization"] = f"Bearer {config.api_key}"
        url = f"{base_url}/chat/completions"
        payload["model"] = config.model
        if config.provider == "openai":
            payload["response_format"] = {"type": "json_object"}
    elif config.provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers["x-api-key"] = config.api_key
        headers["anthropic-version"] = "2023-06-01"
        payload = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
    else:
        raise ValueError(f"Unknown provider: {config.provider}")

    last_error: Optional[Exception] = None
    for attempt in range(config.max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            if config.provider == "anthropic":
                content = data.get("content", [{}])
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", "")
                return str(content)
            else:
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""

        except Exception as e:
            last_error = e
            if attempt < config.max_retries:
                await asyncio.sleep(config.retry_delay)

    raise RuntimeError(f"LLM call failed after {config.max_retries} retries: {last_error}")


def _parse_json_response(raw: str, default: Any = None) -> Any:
    """Parse JSON from LLM response, stripping markdown fences if present."""
    text = raw.strip()
    # Remove markdown code fences
    fence_match = re.match(r"```(?:json)?\s*\n?(.*)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find a JSON object in the text
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return default


# ---------------------------------------------------------------------------
# AgentHarness
# ---------------------------------------------------------------------------


class AgentHarness:
    """Orchestrates the full LLM Agent Pipeline.

    Supports two modes:
      - rule: regex + template-based extraction (no API key needed)
      - llm:  calls OpenAI/Anthropic API for higher quality output
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = AgentLogger()

    # ---- Public API -------------------------------------------------------

    async def run_pipeline(
        self,
        source_text: str,
        source_id: str = "",
        round_num: int = 1,
        mode: Optional[str] = None,
    ) -> PipelineResult:
        """Run the full pipeline on a single source text.

        Args:
            source_text: The raw document text to process.
            source_id: Identifier for this source (used in claim IDs).
            round_num: Experiment round number.
            mode: Override the config mode ("rule" or "llm").

        Returns a PipelineResult with all generated artifacts.
        """
        effective_mode = mode or self.config.mode.value if isinstance(self.config.mode, AgentMode) else self.config.mode
        agent_mode = AgentMode(effective_mode) if isinstance(effective_mode, str) else effective_mode

        result = PipelineResult(round_num=round_num, mode=agent_mode.value)

        # 1. Ingest
        self.logger.log(round_num, "Ingest Agent", f"Processing source {source_id}")
        source_info = await self.run_agent(AgentRole.INGEST, {"text": source_text, "source_id": source_id})
        source_info["source_id"] = source_id or f"SRC-{round_num:03d}-001"
        source_info["round_num"] = round_num
        src = SourceInfo(**{k: v for k, v in source_info.items() if k in SourceInfo.__dataclass_fields__})
        src.full_text = source_text
        result.sources.append(src)

        # 2. Summary
        self.logger.log(round_num, "Summary Agent", f"Generating summary for {source_id}")
        summary_output = await self.run_agent(AgentRole.SUMMARY, {"text": source_text})
        summary_text = summary_output.get("summary", "") if isinstance(summary_output, dict) else str(summary_output)
        result.summaries[source_id] = summary_text
        self.logger.log(round_num, "Summary Agent", f"Generated summary", f"{len(summary_text)} chars")

        # 3. Concept Extraction
        self.logger.log(round_num, "Concept Agent", f"Extracting concepts from {source_id}")
        concept_output = await self.run_agent(AgentRole.CONCEPT, {"text": source_text})
        concepts_raw = concept_output.get("concepts", []) if isinstance(concept_output, dict) else []
        for c_raw in concepts_raw:
            c = ExtractedConcept(
                canonical_name=c_raw.get("canonical_name", ""),
                aliases=c_raw.get("aliases", []),
                definition=c_raw.get("definition", ""),
            )
            result.concepts.append(c)
        self.logger.log(
            round_num, "Concept Agent",
            f"Extracted {len(result.concepts)} concepts",
            ", ".join(c.canonical_name for c in result.concepts),
        )

        # 4. Claim Extraction
        self.logger.log(round_num, "Claim Agent", f"Extracting claims from {source_id}")
        claim_output = await self.run_agent(AgentRole.CLAIM, {"text": source_text, "source_id": source_id})
        claims_raw = claim_output.get("claims", []) if isinstance(claim_output, dict) else []
        for i, c_raw in enumerate(claims_raw):
            claim = ExtractedClaim(
                claim_id=f"CLM-{source_id}-{i:03d}",
                text=c_raw.get("text", ""),
                source_ids=[source_id],
                confidence=c_raw.get("confidence", 0.8),
            )
            result.claims.append(claim)
        self.logger.log(round_num, "Claim Agent", f"Extracted {len(result.claims)} claims")

        # 5. Wiki Writer
        self.logger.log(round_num, "Wiki Writer Agent", f"Generating wiki pages for {source_id}")
        wiki_output = await self.run_agent(
            AgentRole.WIKI_WRITER,
            {
                "text": source_text,
                "source": source_info,
                "concepts": [{"name": c.canonical_name, "definition": c.definition} for c in result.concepts],
                "claims": [{"text": c.text} for c in result.claims],
            },
        )
        if agent_mode == AgentMode.RULE:
            result.wiki_pages = _rule_generate_wiki_pages(
                [src], result.concepts, result.claims, round_num
            )
        else:
            pages_raw = wiki_output.get("pages", []) if isinstance(wiki_output, dict) else []
            for p_raw in pages_raw:
                page = WikiPage(
                    page_id=f"concept_{_slugify(p_raw.get('title', ''))}",
                    title=p_raw.get("title", "Untitled"),
                    content=p_raw.get("content", ""),
                    page_type="concept",
                    round_num=round_num,
                )
                result.wiki_pages.append(page)
        self.logger.log(round_num, "Wiki Writer Agent", f"Generated {len(result.wiki_pages)} wiki pages")

        # 6. Link Builder
        self.logger.log(round_num, "Link Builder Agent", f"Detecting links for round {round_num}")
        link_output = await self.run_agent(
            AgentRole.LINK_BUILDER,
            {"pages": [{"id": p.page_id, "title": p.title, "content": p.content[:500]} for p in result.wiki_pages]},
        )
        if agent_mode == AgentMode.RULE:
            result.links = _rule_detect_links(result.wiki_pages, result.concepts)
        else:
            links_raw = link_output.get("links", []) if isinstance(link_output, dict) else []
            for l_raw in links_raw:
                link = ExtractedLink(
                    source_page_id=l_raw.get("source", ""),
                    target_page_id=l_raw.get("target", ""),
                    link_type=l_raw.get("type", "wikilink"),
                    confidence=l_raw.get("confidence", 0.7),
                )
                result.links.append(link)
        self.logger.log(round_num, "Link Builder Agent", f"Detected {len(result.links)} links")

        # 7. Update Agent (no-op in single-round mode; meaningful in multi-round)
        if round_num > 1:
            self.logger.log(round_num, "Update Agent", f"Checking for updates from round {round_num}")
            update_output = await self.run_agent(
                AgentRole.UPDATE,
                {
                    "existing_pages": [],
                    "new_concepts": [c.canonical_name for c in result.concepts],
                    "round_num": round_num,
                },
            )
            self.logger.log(round_num, "Update Agent", f"Update check complete")

        return result

    async def run_pipeline_batch(
        self,
        sources: list[dict[str, str]],
        round_num: int = 1,
        mode: Optional[str] = None,
    ) -> PipelineResult:
        """Run pipeline on multiple source texts and merge results."""
        all_results: list[PipelineResult] = []
        for i, src_dict in enumerate(sources):
            source_text = src_dict.get("text", "") or src_dict.get("content", "")
            source_id = src_dict.get("source_id", "") or f"SRC-{round_num:03d}-{i + 1:03d}"
            result = await self.run_pipeline(source_text, source_id, round_num, mode)
            all_results.append(result)

        # Merge
        merged = PipelineResult(round_num=round_num, mode=mode or self.config.mode.value)
        for r in all_results:
            merged.sources.extend(r.sources)
            merged.summaries.update(r.summaries)
            merged.concepts.extend(r.concepts)
            merged.claims.extend(r.claims)
            merged.wiki_pages.extend(r.wiki_pages)
            merged.links.extend(r.links)
            merged.errors.extend(r.errors)

        # Deduplicate concepts by canonical name
        seen_names: set[str] = set()
        unique_concepts: list[ExtractedConcept] = []
        for c in merged.concepts:
            if c.canonical_name not in seen_names:
                seen_names.add(c.canonical_name)
                unique_concepts.append(c)
        merged.concepts = unique_concepts

        return merged

    async def run_agent(self, role: AgentRole, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run a single agent role.

        In rule mode, uses deterministic regex + template extraction.
        In LLM mode, calls the configured API with structured output parsing.
        """
        if self.config.mode == AgentMode.RULE or (
            isinstance(self.config.mode, str) and self.config.mode == "rule"
        ):
            return self._run_agent_rule(role, input_data)
        else:
            return await self._run_agent_llm(role, input_data)

    # ---- Rule-mode dispatch ----------------------------------------------

    def _run_agent_rule(self, role: AgentRole, input_data: dict[str, Any]) -> dict[str, Any]:
        text = input_data.get("text", "") or input_data.get("content", "")
        source_id = input_data.get("source_id", "SRC-000")

        if role == AgentRole.INGEST:
            return _rule_extract_bibliographic(text)
        elif role == AgentRole.SUMMARY:
            return {"summary": _rule_generate_summary(text)}
        elif role == AgentRole.CONCEPT:
            concepts = _rule_extract_concepts(text)
            return {
                "concepts": [
                    {"canonical_name": c.canonical_name, "aliases": c.aliases, "definition": c.definition}
                    for c in concepts
                ]
            }
        elif role == AgentRole.CLAIM:
            claims = _rule_extract_claims(text, source_id)
            return {
                "claims": [
                    {"text": c.text, "confidence": c.confidence} for c in claims
                ]
            }
        elif role == AgentRole.WIKI_WRITER:
            # This is handled in run_pipeline directly
            return {"pages": []}
        elif role == AgentRole.LINK_BUILDER:
            return {"links": []}
        elif role == AgentRole.UPDATE:
            return {"updates": []}
        else:
            return {}

    # ---- LLM-mode dispatch -----------------------------------------------

    async def _run_agent_llm(self, role: AgentRole, input_data: dict[str, Any]) -> dict[str, Any]:
        system_prompt = SYSTEM_PROMPTS.get(role, "You are a helpful research assistant.")
        text = input_data.get("text", "") or input_data.get("content", "")
        source_id = input_data.get("source_id", "")

        user_prompt = f"Source ID: {source_id}\n\nText:\n{text[:8000]}"

        raw = await _call_llm(self.config, system_prompt, user_prompt)
        parsed = _parse_json_response(raw, default={})
        return parsed if isinstance(parsed, dict) else {}

    # ---- Diagnostic agent query (ask about the KB) -----------------------

    async def ask_diagnostic_agent(
        self,
        question: str,
        kb_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Ask the diagnostic agent a question about the current knowledge base state.

        This is the endpoint behind the xAI Agent Panel. It analyzes current
        KB metrics, issues, and structure to provide informed answers.

        Args:
            question: Natural language question from the user.
            kb_context: Dict with keys like round_name, metrics, issues, graph_stats.

        Returns a dict with keys: answer, sources.
        """
        system_prompt = textwrap.dedent("""\
            You are the AgentKB-Diag diagnostic agent. Your job is to analyze
            the health of an LLM-agent-maintained wiki knowledge base and answer
            questions about its structure, retrieval performance, and degradation.

            Be concise and evidence-based. When possible, cite specific metrics,
            issue counts, or page names from the provided KB context.

            Return a JSON object with:
              - answer: your diagnostic analysis (2-5 sentences)
              - sources: list of specific page_ids or issue_ids referenced
            Always output valid JSON only, no commentary.""")

        # In rule mode, generate a rule-based diagnostic answer
        if self.config.mode == AgentMode.RULE or (
            isinstance(self.config.mode, str) and self.config.mode == "rule"
        ):
            return self._rule_diagnostic_answer(question, kb_context)

        context_str = json.dumps(kb_context, ensure_ascii=False, indent=2)
        user_prompt = f"KB Context:\n{context_str}\n\nQuestion: {question}"

        raw = await _call_llm(self.config, system_prompt, user_prompt)
        parsed = _parse_json_response(raw, default={})
        if isinstance(parsed, dict):
            return parsed
        return {"answer": raw, "sources": []}

    def _rule_diagnostic_answer(self, question: str, kb_context: dict[str, Any]) -> dict[str, Any]:
        """Generate a rule-based diagnostic answer without API calls."""
        metrics = kb_context.get("metrics", {})
        issues = kb_context.get("issues", [])
        issue_count = len(issues) if isinstance(issues, list) else 0

        q_lower = question.lower()
        answer = ""
        sources: list[str] = []

        if "recall" in q_lower or "r@3" in q_lower or "retriev" in q_lower:
            recall = metrics.get("recall_at_3", 0)
            if recall < 0.6:
                answer = (
                    f"Recall@3 is {recall:.2f}, which is below the healthy threshold of 0.70. "
                    f"This degradation is primarily driven by orphan concepts (no incoming links) "
                    f"and duplicate pages that fragment the retrieval signal. "
                    f"Addressing the {issue_count} detected issues should restore recall."
                )
            elif recall < 0.8:
                answer = (
                    f"Recall@3 is {recall:.2f}, moderately degraded. "
                    f"The main contributors are likely orphan pages and broken links. "
                    f"Review the {issue_count} issues flagged by the diagnosis system."
                )
            else:
                answer = (
                    f"Recall@3 is {recall:.2f}, which is healthy. "
                    f"No critical retrieval issues detected."
                )
            sources = ["diagnosis_metrics", "retrieval_evaluation"]

        elif "issue" in q_lower or "problem" in q_lower or "top" in q_lower:
            if issue_count == 0:
                answer = "No issues detected in the current knowledge base state."
            else:
                issue_types: dict[str, int] = {}
                if isinstance(issues, list):
                    for issue in issues:
                        t = issue.get("type", "unknown") if isinstance(issue, dict) else getattr(issue, "type", "unknown")
                        issue_types[t] = issue_types.get(t, 0) + 1

                type_summary = ", ".join(f"{k}: {v}" for k, v in issue_types.items())
                answer = (
                    f"Found {issue_count} issues across {len(issue_types)} types: {type_summary}. "
                    f"Orphan pages are the most critical as they directly reduce recall. "
                    f"Duplicates fragment knowledge and confuse retrieval ranking. "
                    f"Conflicts erode trust in claims. Prioritize fixing orphans first."
                )
            sources = ["diagnosis_issues"]

        elif "orphan" in q_lower:
            orphan_count = 0
            if isinstance(issues, list):
                orphan_count = sum(
                    1 for i in issues
                    if (isinstance(i, dict) and i.get("type") == "orphan")
                    or (hasattr(i, "type") and i.type == "orphan")
                )
            answer = (
                f"There are {orphan_count} orphan pages — concepts with no incoming links. "
                f"Orphans are unreachable through graph traversal and effectively invisible "
                f"to retrieval. The fix is to add [[wikilink]] references from related concept "
                f"pages back to the orphan. This is the highest-impact repair for recall."
            )
            sources = ["diagnosis_issues", "knowledge_graph"]

        elif "duplicate" in q_lower:
            dup_count = 0
            if isinstance(issues, list):
                dup_count = sum(
                    1 for i in issues
                    if (isinstance(i, dict) and i.get("type") == "duplicate")
                    or (hasattr(i, "type") and i.type == "duplicate")
                )
            answer = (
                f"Found {dup_count} duplicate concept pages. Duplicates split the retrieval "
                f"score across multiple pages for the same concept, reducing ranking precision. "
                f"Merge duplicates into a single canonical page with cross-references."
            )
            sources = ["diagnosis_issues"]

        elif "conflict" in q_lower:
            conflict_count = 0
            if isinstance(issues, list):
                conflict_count = sum(
                    1 for i in issues
                    if (isinstance(i, dict) and i.get("type") == "conflict")
                    or (hasattr(i, "type") and i.type == "conflict")
                )
            answer = (
                f"There are {conflict_count} conflicting claims. Conflicts arise when "
                f"different sources make contradictory assertions that are both recorded "
                f"as claims. Resolve by adding consensus annotations or scoping claims "
                f"to specific models/benchmarks."
            )
            sources = ["diagnosis_issues"]

        else:
            answer = (
                f"The knowledge base currently has {issue_count} detected issues across "
                f"orphan, duplicate, conflict, and missing citation categories. "
                f"Recall@3 is {metrics.get('recall_at_3', 'N/A')}. "
                f"You can ask me about specific issues (orphans, duplicates, conflicts) "
                f"or retrieval performance for more targeted analysis."
            )
            sources = ["diagnosis_summary"]

        return {"answer": answer, "sources": sources}


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_harness_from_settings() -> AgentHarness:
    """Create an AgentHarness from the application Settings singleton."""
    from app.core.config import settings

    config = AgentConfig(
        provider=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        mode=AgentMode(settings.agent_default_mode),
        max_retries=settings.agent_max_retries,
        retry_delay=settings.agent_retry_delay_seconds,
    )
    return AgentHarness(config)
