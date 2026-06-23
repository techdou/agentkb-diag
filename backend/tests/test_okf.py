"""
Tests for OKF v0.1 compliance of the agent pipeline generators.

Verifies that the rule-mode wiki page generator produces OKF-conformant
documents: frontmatter with required `type` field, standard markdown links
(no [[wikilink]]), and correct page structure.
"""

import re

from app.services.agent_harness import (
    ExtractedClaim,
    ExtractedConcept,
    SourceInfo,
    WikiPage,
    _rule_generate_wiki_pages,
    _rule_detect_links,
    _emit_okf_frontmatter,
)


def _make_source(source_id: str, title: str, concept_name: str) -> SourceInfo:
    return SourceInfo(
        source_id=source_id,
        title=title,
        authors=["Test Author"],
        year=2024,
        tags=["test"],
        abstract=f"This paper discusses {concept_name} in depth.",
        full_text=f"{concept_name} is the focus of this work on retrieval.",
    )


def _make_concept(name: str) -> ExtractedConcept:
    return ExtractedConcept(
        canonical_name=name,
        aliases=[f"{name} alias"],
        definition=f"{name} is a test concept for RAG research.",
    )


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TYPE_RE = re.compile(r"^type:\s*(\S+)", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


class TestOkfFrontmatter:
    def test_frontmatter_has_required_type(self):
        fm = _emit_okf_frontmatter({"type": "Concept", "title": "RAG"})
        m = FRONTMATTER_RE.match(fm + "\n\nbody")
        assert m is not None
        type_match = TYPE_RE.search(m.group(1))
        assert type_match is not None
        assert type_match.group(1) == "Concept"

    def test_frontmatter_skips_missing_keys(self):
        fm = _emit_okf_frontmatter({"type": "Concept"})
        assert "type:" in fm
        # keys not in the allowed/required set should be absent
        assert "aliases:" not in fm

    def test_frontmatter_quotes_strings(self):
        fm = _emit_okf_frontmatter({"type": "Concept", "title": "Test"})
        assert 'title: "Test"' in fm


class TestRuleWikiGeneration:
    def test_concept_pages_have_okf_frontmatter(self):
        sources = [_make_source("001", "Paper One", "RAG")]
        concepts = [_make_concept("RAG")]
        claims = [
            ExtractedClaim(
                claim_id="claim_001",
                text="RAG improves retrieval quality",
                source_ids=["001"],
                status="supported",
            )
        ]
        pages = _rule_generate_wiki_pages(sources, concepts, claims, round_num=1)
        concept_pages = [p for p in pages if p.page_type == "concept"]
        assert len(concept_pages) == 1

        m = FRONTMATTER_RE.match(concept_pages[0].content)
        assert m is not None, "concept page missing frontmatter"
        type_match = TYPE_RE.search(m.group(1))
        assert type_match is not None
        assert type_match.group(1) == "Concept"

    def test_source_pages_have_okf_frontmatter(self):
        sources = [_make_source("001", "Paper One", "RAG")]
        concepts = [_make_concept("RAG")]
        pages = _rule_generate_wiki_pages(sources, concepts, [], round_num=1)
        source_pages = [p for p in pages if p.page_type == "source"]
        assert len(source_pages) == 1

        m = FRONTMATTER_RE.match(source_pages[0].content)
        assert m is not None
        type_match = TYPE_RE.search(m.group(1))
        assert type_match.group(1) == "Source"

    def test_no_wikilink_syntax_in_generated_pages(self):
        sources = [_make_source("001", "Paper One", "RAG")]
        concepts = [_make_concept("RAG")]
        pages = _rule_generate_wiki_pages(sources, concepts, [], round_num=1)
        for page in pages:
            assert not WIKILINK_RE.search(page.content), (
                f"page {page.page_id} contains [[wikilink]]"
            )

    def test_source_links_are_standard_markdown(self):
        sources = [_make_source("001", "Paper One", "RAG")]
        concepts = [_make_concept("RAG")]
        pages = _rule_generate_wiki_pages(sources, concepts, [], round_num=1)
        concept_page = next(p for p in pages if p.page_type == "concept")
        # Related Sources section should use [text](/sources/...) links.
        if "## Related Sources" in concept_page.content:
            assert re.search(
                r"\[[^\]]+\]\(/sources/source_001\.md\)", concept_page.content
            ), "source links should be standard markdown, not [[wikilink]]"

    def test_claim_anchors_use_html_id(self):
        sources = [_make_source("001", "Paper One", "RAG")]
        concepts = [_make_concept("RAG")]
        claims = [
            ExtractedClaim(
                claim_id="claim_001",
                text="RAG improves retrieval quality",
                source_ids=["001"],
                status="supported",
            )
        ]
        pages = _rule_generate_wiki_pages(sources, concepts, claims, round_num=1)
        concept_page = next(p for p in pages if p.page_type == "concept")
        assert '<a id="claim_001"></a>' in concept_page.content


class TestRuleLinkDetection:
    def test_default_link_type_is_references(self):
        sources = [_make_source("001", "Paper One", "RAG")]
        concepts = [_make_concept("RAG")]
        claims = [
            ExtractedClaim(
                claim_id="claim_001",
                text="RAG improves retrieval quality",
                source_ids=["001"],
                status="supported",
            )
        ]
        pages = _rule_generate_wiki_pages(sources, concepts, claims, round_num=1)
        links = _rule_detect_links(pages, concepts)
        # No wikilink type should appear; default is references.
        for link in links:
            assert link.link_type != "wikilink", (
                f"link {link.source_page_id}->{link.target_page_id} still wikilink"
            )


class TestExportedBundleConformance:
    """Smoke-test that the shipped okf/ bundle still passes conformance."""

    def test_bundle_conformant(self):
        import sys
        from pathlib import Path

        backend_dir = Path(__file__).resolve().parent.parent
        scripts_dir = backend_dir / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        import okf_check

        bundle = backend_dir.parent / "okf"
        if not bundle.exists():
            return  # bundle not built in this environment; skip
        # check_bundle prints + returns exit code; capture by redirecting.
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = okf_check.check_bundle(bundle)
        assert rc == 0, f"OKF bundle non-conformant:\n{buf.getvalue()}"
