from pydantic import BaseModel


class Source(BaseModel):
    source_id: str
    title: str
    authors: list[str] = []
    year: int
    round: int
    tags: list[str] = []
    path: str = ""


class Claim(BaseModel):
    claim_id: str
    text: str
    page_id: str
    source_ids: list[str] = []
    round_created: int
    round_updated: int
    status: str = "supported"  # supported, unsupported, conflicted


class Concept(BaseModel):
    concept_id: str
    canonical_name: str
    aliases: list[str] = []
    page_id: str
    round_created: int
    round_updated: int


class GraphNode(BaseModel):
    id: str
    type: str = "concept_page"
    label: str
    round_created: int
    issue_flags: list[str] = []


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str = "wikilink"
    round_created: int
    confidence: float = 1.0


class LinkGraph(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class AliasEntry(BaseModel):
    alias: str
    canonical: str
    confidence: float
    status: str = "suggested"


class RetrievalTest(BaseModel):
    query_id: str
    query: str
    expected_pages: list[str] = []
    expected_claims: list[str] = []
    query_type: str = "concept_explanation"


class HealthReport(BaseModel):
    round_name: str
    citation_coverage: float
    unsupported_claim_rate: float
    orphan_rate: float
    duplicate_rate: float
    conflict_density: float
    recall_at_3: float
    mrr: float
    page_count: int
    claim_count: int
    source_count: int
    issue_count: int


class Issue(BaseModel):
    issue_id: str
    type: str  # orphan, duplicate, conflict, broken_link, missing_citation
    severity: str  # high, medium, low
    page_id: str
    description: str
    suggestion: str


class SearchResult(BaseModel):
    page_id: str
    score: float
    hit: bool


class RetrievalResult(BaseModel):
    query_id: str
    query: str
    expected_pages: list[str]
    retrieved_pages: list[SearchResult]
    all_hit: bool
    failure_reasons: list[str] = []
    suggestions: list[str] = []


class FailureAttribution(BaseModel):
    reason: str
    detail: str
    suggestion: str


class MethodResult(BaseModel):
    method: str  # raw_doc_rag, static_wiki, agent_wiki, agentkb_diag
    recall_at_3: float
    mrr: float
    total_queries: int
    passed_queries: int
    description: str = ""


class MethodComparison(BaseModel):
    round_name: str
    methods: list[MethodResult]
    queries: list[dict] = []  # per-query breakdown


class CaseStudy(BaseModel):
    case_id: str
    title: str
    phenomenon: str
    diagnosis: str
    repair: str
    before_metric: float
    after_metric: float
    relevant_pages: list[str] = []
    relevant_query_ids: list[str] = []


class RoundResult(BaseModel):
    round_name: str
    health_report: HealthReport
    method_comparison: MethodComparison
    status: str = "completed"
    error: str = ""
    artifacts: list[str] = []
