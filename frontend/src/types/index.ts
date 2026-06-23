export interface HealthReport {
  round_name: string;
  citation_coverage: number;
  unsupported_claim_rate: number;
  orphan_rate: number;
  duplicate_rate: number;
  conflict_density: number;
  recall_at_3: number;
  mrr: number;
  page_count: number;
  claim_count: number;
  source_count: number;
  issue_count: number;
}

export interface Issue {
  issue_id: string;
  type: 'orphan' | 'duplicate' | 'conflict' | 'broken_link' | 'missing_citation';
  severity: 'high' | 'medium' | 'low';
  page_id: string;
  description: string;
  suggestion: string;
}

export interface SearchResult {
  page_id: string;
  score: number;
  hit: boolean;
}

export interface RetrievalResult {
  query_id: string;
  query: string;
  expected_pages: string[];
  retrieved_pages: SearchResult[];
  all_hit: boolean;
  failure_reasons: string[];
  suggestions: string[];
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  round_created: number;
  issue_flags: string[];
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  round_created: number;
  confidence: number;
}

export interface LinkGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Claim {
  claim_id: string;
  text: string;
  page_id: string;
  source_ids: string[];
  round_created: number;
  round_updated: number;
  status: string;
}

export interface FailureAnalysis {
  query_id: string;
  query_text: string;
  round: string;
  expected_pages: string[];
  expected_claims: string[];
  retrieved_pages: SearchResult[];
  all_hit: boolean;
  failure_reasons: { type: string; description: string }[];
  suggestions: string[];
}

export interface MethodResult {
  method: string;
  recall_at_3: number;
  mrr: number;
  total_queries: number;
  passed_queries: number;
  description: string;
}

export interface MethodComparison {
  round_name: string;
  methods: MethodResult[];
  queries: Record<string, unknown>[];
}

export interface CaseStudy {
  case_id: string;
  title: string;
  phenomenon: string;
  diagnosis: string;
  repair: string;
  before_metric: number;
  after_metric: number;
  relevant_pages: string[];
  relevant_query_ids: string[];
}

export interface RoundResult {
  round_name: string;
  health_report: HealthReport;
  method_comparison: MethodComparison;
  status: string;
  error: string;
  artifacts: string[];
}

export type RoundName = 'round_1' | 'round_2' | 'round_3' | 'repair';
export type SidebarView = 'overview' | 'structure' | 'provenance' | 'failure' | 'experiment';
