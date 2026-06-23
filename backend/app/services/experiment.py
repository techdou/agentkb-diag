"""
ExperimentService provides management of experiment rounds,
method comparison, case studies, and data export functionality.
"""

import csv
import io
import json
import os
from pathlib import Path
from typing import Optional

from app.models.schemas import (
    HealthReport,
    MethodResult,
    MethodComparison,
    CaseStudy,
    RoundResult,
)
from app.services.data_store import store
from app.services.diagnosis import diagnosis_service
from app.services.baselines import (
    RawDocRAG,
    StaticWikiRAG,
    AgentWikiRAG,
    AgentKBDiag,
    compute_baseline_metrics,
    BaselineRetriever,
)

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
PROJECT_ROOT = BACKEND_DIR.parent  # agentkb-diag/
REPORTS_DIR = PROJECT_ROOT / "workspace" / "reports"


class ExperimentService:
    """Manages experiment rounds, metrics comparison, method comparison, and exports."""

    def __init__(self):
        self._case_studies_cache: Optional[list[CaseStudy]] = None

    def get_rounds(self) -> list[str]:
        """Return sorted list of available round names."""
        return store.get_round_names()

    def get_metrics(self) -> list[HealthReport]:
        """Compute and return HealthReports for all available rounds."""
        round_names = self.get_rounds()
        reports = []
        for name in round_names:
            report = diagnosis_service.compute_all_metrics(name)
            reports.append(report)
        return reports

    # ── Method Comparison ──────────────────────────────────────────

    @staticmethod
    def _build_source_to_concepts() -> dict[str, set[str]]:
        """Map source_id -> set of concept page_ids whose claims cite that source.

        Lets RawDocRAG (which retrieves source documents) be scored against
        concept-level expectations."""
        mapping: dict[str, set[str]] = {}
        for claim in store.get_claims():
            for sid in claim.source_ids:
                mapping.setdefault(sid, set()).add(claim.page_id)
        return mapping

    def run_method_comparison(self, round_name: str) -> MethodComparison:
        """
        Run all 4 retrieval methods against all test queries for a given round.

        Each method is a real retriever instance (no synthetic offsets):
          - raw_doc_rag: TF-IDF over raw source documents
          - static_wiki: TF-IDF over the Round 1 wiki snapshot (frozen)
          - agent_wiki: TF-IDF over the current round's wiki
          - agentkb_diag: agent_wiki + diagnosis-driven repairs
        """
        descriptions = {
            "raw_doc_rag": "Direct source document TF-IDF index, no wiki structure",
            "static_wiki": "Round 1 wiki pages only, frozen (no updates)",
            "agent_wiki": "Agent-built wiki at current round (no repair)",
            "agentkb_diag": "Agent-built wiki + diagnosis-driven repair",
        }

        tests = store.get_tests()
        test_queries = [
            {"query_id": t.query_id, "query": t.query} for t in tests
        ]
        expected_map = {t.query_id: set(t.expected_pages) for t in tests}
        source_map = self._build_source_to_concepts()

        # Instantiate each retriever. RawDocRAG indexes raw documents; the wiki
        # retrievers index concept pages and need the round context.
        data_paths = {"round_name": round_name}
        retrievers: list[tuple[str, BaselineRetriever, Optional[dict]]] = [
            ("raw_doc_rag", RawDocRAG(), source_map),
            ("static_wiki", StaticWikiRAG(), None),
            ("agent_wiki", AgentWikiRAG(data_paths), None),
            ("agentkb_diag", AgentKBDiag(data_paths), None),
        ]

        method_results: list[MethodResult] = []
        for method, retriever, id_mapper in retrievers:
            metrics = compute_baseline_metrics(
                retriever=retriever,
                test_queries=test_queries,
                expected_map=expected_map,
                top_k=3,
                id_mapper=id_mapper,
            )
            method_results.append(MethodResult(
                method=method,
                recall_at_3=round(metrics["recall_at_k"], 4),
                mrr=round(metrics["mrr"], 4),
                total_queries=metrics["total_queries"],
                passed_queries=metrics["passed_queries"],
                description=descriptions.get(method, ""),
            ))

        return MethodComparison(
            round_name=round_name,
            methods=method_results,
            queries=[],
        )

    def get_full_comparison(self) -> list[dict]:
        """
        Get comparison across all rounds x all 4 methods.
        Returns data for the full experiment table showing degradation and repair.
        """
        rounds = self.get_rounds()
        results: list[dict] = []

        for rname in rounds:
            comparison = self.run_method_comparison(rname)
            row: dict = {"round_name": rname}
            for m in comparison.methods:
                row[f"{m.method}_recall_at_3"] = m.recall_at_3
                row[f"{m.method}_mrr"] = m.mrr
                row[f"{m.method}_passed"] = m.passed_queries
            results.append(row)

        return results

    # ── Case Studies ───────────────────────────────────────────────

    def get_case_studies(self) -> list[CaseStudy]:
        """Return 4 paper-level case studies. Loads from JSON file if available."""
        if self._case_studies_cache is not None:
            return self._case_studies_cache

        # Try loading from workspace/reports/case_studies.json
        case_file = REPORTS_DIR / "case_studies.json"
        if case_file.exists():
            try:
                with open(case_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self._case_studies_cache = [CaseStudy(**c) for c in raw]
                return self._case_studies_cache
            except (json.JSONDecodeError, OSError):
                pass

        # Fallback: empty list if JSON unavailable
        self._case_studies_cache = []
        return self._case_studies_cache

    # ── Round Runner ───────────────────────────────────────────────

    def run_round(self, round_name: str) -> HealthReport:
        """Run diagnosis for a specific round and return its HealthReport."""
        return diagnosis_service.compute_all_metrics(round_name)

    def run_full_round(self, round_name: str) -> RoundResult:
        """
        Full pipeline for a round:
          build snapshot → diagnose → evaluate retrieval → compare methods → snapshot
        """
        errors: list[str] = []
        artifacts: list[str] = []

        # 1. Build health report
        try:
            health = diagnosis_service.compute_all_metrics(round_name)
            artifacts.append(f"health_report_{round_name}")
        except Exception as e:
            errors.append(f"Health report failed: {e}")
            health = HealthReport(
                round_name=round_name,
                citation_coverage=0.0,
                unsupported_claim_rate=0.0,
                orphan_rate=0.0,
                duplicate_rate=0.0,
                conflict_density=0.0,
                recall_at_3=0.0,
                mrr=0.0,
                page_count=0,
                claim_count=0,
                source_count=0,
                issue_count=0,
            )

        # 2. Run method comparison
        try:
            comparison = self.run_method_comparison(round_name)
            artifacts.append(f"method_comparison_{round_name}")
        except Exception as e:
            errors.append(f"Method comparison failed: {e}")
            comparison = MethodComparison(round_name=round_name, methods=[], queries=[])

        status = "completed" if not errors else "partial"
        return RoundResult(
            round_name=round_name,
            health_report=health,
            method_comparison=comparison,
            status=status,
            error="; ".join(errors) if errors else "",
            artifacts=artifacts,
        )

    # ── Export ─────────────────────────────────────────────────────

    def export_csv(self) -> str:
        """Generate a CSV string of all rounds' metrics plus method comparison."""
        reports = self.get_metrics()
        output = io.StringIO()
        if not reports:
            hdr = ("round_name,citation_coverage,unsupported_claim_rate,orphan_rate,"
                   "duplicate_rate,conflict_density,recall_at_3,mrr,page_count,"
                   "claim_count,source_count,issue_count\n")
            return hdr

        fieldnames = [
            "round_name", "citation_coverage", "unsupported_claim_rate",
            "orphan_rate", "duplicate_rate", "conflict_density",
            "recall_at_3", "mrr", "page_count", "claim_count",
            "source_count", "issue_count",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for report in reports:
            writer.writerow(report.model_dump())
        return output.getvalue()

    def export_json(self) -> str:
        """Generate a JSON string of all rounds' metrics plus method comparisons."""
        reports = self.get_metrics()
        report_data = [r.model_dump() for r in reports]

        # Add full comparison data
        try:
            full_comp = self.get_full_comparison()
        except Exception:
            full_comp = []

        export = {
            "rounds": report_data,
            "method_comparisons": full_comp,
        }
        return json.dumps(export, indent=2, ensure_ascii=False)


# Module-level singleton
experiment_service = ExperimentService()
