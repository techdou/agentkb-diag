import type {
  HealthReport,
  Issue,
  SearchResult,
  RetrievalResult,
  GraphNode,
  GraphEdge,
  LinkGraph,
  Claim,
  FailureAnalysis,
  MethodComparison,
  MethodResult,
  CaseStudy,
  RoundResult,
} from '../types';

const USE_MOCK = false;

// ── Real API fetch ────────────────────────────────────────────────

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// ── Fallback mock data (RAG concepts) ──────────────────────────────

const RAG_NODES: GraphNode[] = [
  { id: 'RAG', type: 'concept', label: 'RAG', round_created: 1, issue_flags: [] },
  { id: 'GraphRAG', type: 'concept', label: 'GraphRAG', round_created: 1, issue_flags: [] },
  { id: 'Agentic_RAG', type: 'concept', label: 'Agentic_RAG', round_created: 2, issue_flags: [] },
  { id: 'Dense_Retrieval', type: 'concept', label: 'Dense_Retrieval', round_created: 1, issue_flags: [] },
  { id: 'Self_RAG', type: 'concept', label: 'Self_RAG', round_created: 2, issue_flags: ['duplicate'] },
  { id: 'Corrective_RAG', type: 'concept', label: 'Corrective_RAG', round_created: 2, issue_flags: ['duplicate'] },
  { id: 'KG_RAG', type: 'concept', label: 'KG_RAG', round_created: 3, issue_flags: [] },
  { id: 'Citation_Faithfulness', type: 'concept', label: 'Citation_Faithfulness', round_created: 3, issue_flags: ['orphan'] },
  { id: 'Multi_Hop_Retrieval', type: 'concept', label: 'Multi_Hop_Retrieval', round_created: 2, issue_flags: [] },
  { id: 'RAG_Evaluation', type: 'concept', label: 'RAG_Evaluation', round_created: 1, issue_flags: [] },
  { id: 'Long_Context', type: 'concept', label: 'Long_Context', round_created: 3, issue_flags: ['conflict'] },
  { id: 'KB_Degradation', type: 'concept', label: 'KB_Degradation', round_created: 3, issue_flags: [] },
  { id: 'Multimodal_RAG', type: 'concept', label: 'Multimodal_RAG', round_created: 3, issue_flags: ['orphan'] },
];

const RAG_EDGES: GraphEdge[] = [
  { source: 'RAG', target: 'Dense_Retrieval', type: 'uses', round_created: 1, confidence: 0.95 },
  { source: 'RAG', target: 'RAG_Evaluation', type: 'related', round_created: 1, confidence: 0.85 },
  { source: 'RAG', target: 'Multi_Hop_Retrieval', type: 'related', round_created: 2, confidence: 0.80 },
  { source: 'GraphRAG', target: 'KG_RAG', type: 'related', round_created: 3, confidence: 0.90 },
  { source: 'RAG', target: 'GraphRAG', type: 'related', round_created: 1, confidence: 0.88 },
  { source: 'Self_RAG', target: 'Corrective_RAG', type: 'related', round_created: 2, confidence: 0.70 },
  { source: 'Agentic_RAG', target: 'RAG', type: 'extends', round_created: 2, confidence: 0.92 },
  { source: 'RAG', target: 'KB_Degradation', type: 'related', round_created: 3, confidence: 0.75 },
  { source: 'Long_Context', target: 'RAG', type: 'related', round_created: 3, confidence: 0.65 },
  { source: 'Dense_Retrieval', target: 'Multi_Hop_Retrieval', type: 'related', round_created: 2, confidence: 0.78 },
  { source: 'RAG', target: 'Multimodal_RAG', type: 'extends', round_created: 3, confidence: 0.72 },
  { source: 'RAG', target: 'Citation_Faithfulness', type: 'related', round_created: 3, confidence: 0.68 },
  { source: 'RAG', target: 'Long_Context', type: 'related', round_created: 3, confidence: 0.60 },
  { source: 'GraphRAG', target: 'Agentic_RAG', type: 'related', round_created: 2, confidence: 0.55 },
  { source: 'Self_RAG', target: 'Agentic_RAG', type: 'related', round_created: 2, confidence: 0.50 },
  { source: 'KG_RAG', target: 'GraphRAG', type: 'extends', round_created: 3, confidence: 0.85 },
];

const RAG_HEALTH_REPORTS: HealthReport[] = [
  {
    round_name: 'round_1',
    citation_coverage: 0.85,
    unsupported_claim_rate: 0.10,
    orphan_rate: 0.10,
    duplicate_rate: 0.05,
    conflict_density: 0.00,
    recall_at_3: 0.85,
    mrr: 0.78,
    page_count: 32,
    claim_count: 95,
    source_count: 62,
    issue_count: 8,
  },
  {
    round_name: 'round_2',
    citation_coverage: 0.78,
    unsupported_claim_rate: 0.15,
    orphan_rate: 0.15,
    duplicate_rate: 0.10,
    conflict_density: 0.10,
    recall_at_3: 0.72,
    mrr: 0.65,
    page_count: 48,
    claim_count: 140,
    source_count: 88,
    issue_count: 18,
  },
  {
    round_name: 'round_3',
    citation_coverage: 0.62,
    unsupported_claim_rate: 0.28,
    orphan_rate: 0.28,
    duplicate_rate: 0.25,
    conflict_density: 0.40,
    recall_at_3: 0.55,
    mrr: 0.48,
    page_count: 65,
    claim_count: 195,
    source_count: 105,
    issue_count: 34,
  },
  {
    round_name: 'repair',
    citation_coverage: 0.80,
    unsupported_claim_rate: 0.12,
    orphan_rate: 0.12,
    duplicate_rate: 0.08,
    conflict_density: 0.10,
    recall_at_3: 0.78,
    mrr: 0.72,
    page_count: 60,
    claim_count: 185,
    source_count: 120,
    issue_count: 12,
  },
];

const RAG_ISSUES: Issue[] = [
  {
    issue_id: 'ISS-001',
    type: 'orphan',
    severity: 'high',
    page_id: 'Citation_Faithfulness',
    description: 'Page "Citation_Faithfulness" has no incoming links — unreachable via navigation or retrieval',
    suggestion: 'Add links from RAG and RAG_Evaluation pages to Citation_Faithfulness',
  },
  {
    issue_id: 'ISS-002',
    type: 'orphan',
    severity: 'high',
    page_id: 'Multimodal_RAG',
    description: 'Page "Multimodal_RAG" has no incoming links — isolated from the knowledge graph',
    suggestion: 'Add backlinks from RAG, Dense_Retrieval, and GraphRAG concept pages',
  },
  {
    issue_id: 'ISS-003',
    type: 'duplicate',
    severity: 'medium',
    page_id: 'Self_RAG',
    description: 'Self_RAG and Corrective_RAG describe overlapping concepts with shared terminology',
    suggestion: 'Merge Self_RAG into Corrective_RAG as a subsection, or create a canonical page for both',
  },
  {
    issue_id: 'ISS-004',
    type: 'duplicate',
    severity: 'medium',
    page_id: 'Corrective_RAG',
    description: 'Corrective_RAG overlaps significantly with Self_RAG — redundant knowledge fragments',
    suggestion: 'Merge into a unified "Self-Corrective RAG" page with cross-references',
  },
  {
    issue_id: 'ISS-005',
    type: 'conflict',
    severity: 'high',
    page_id: 'Long_Context',
    description: 'Contradictory claims about long-context effectiveness: one claim says LLMs maintain >90% accuracy at 128K tokens; another says accuracy degrades to <60% beyond 32K',
    suggestion: 'Reconcile claims with specific model/benchmark context, add consensus annotation',
  },
  {
    issue_id: 'ISS-006',
    type: 'broken_link',
    severity: 'medium',
    page_id: 'KB_Degradation',
    description: 'Reference link to "Retrievability_Metrics" page is broken — page was renamed to RAG_Evaluation',
    suggestion: 'Update link to point to RAG_Evaluation or create an alias mapping',
  },
  {
    issue_id: 'ISS-007',
    type: 'missing_citation',
    severity: 'low',
    page_id: 'Agentic_RAG',
    description: 'Claim "agentic retrieval improves recall by 15-20%" lacks source citation',
    suggestion: 'Add citation to the relevant benchmark paper (e.g., IRCoT, ReAct, or DSPy)',
  },
];

const RAG_RETRIEVAL_RESULTS: RetrievalResult[] = [
  {
    query_id: 'QRY-001',
    query: 'How does RAG compare to GraphRAG for multi-hop retrieval?',
    expected_pages: ['RAG', 'GraphRAG', 'Multi_Hop_Retrieval'],
    retrieved_pages: [
      { page_id: 'RAG', score: 0.92, hit: true },
      { page_id: 'GraphRAG', score: 0.78, hit: true },
      { page_id: 'Dense_Retrieval', score: 0.64, hit: false },
      { page_id: 'Multi_Hop_Retrieval', score: 0.51, hit: true },
      { page_id: 'KG_RAG', score: 0.33, hit: false },
    ],
    all_hit: true,
    failure_reasons: [],
    suggestions: [],
  },
  {
    query_id: 'QRY-002',
    query: 'What are the known problems with agent-maintained knowledge bases?',
    expected_pages: ['KB_Degradation', 'Citation_Faithfulness', 'RAG_Evaluation'],
    retrieved_pages: [
      { page_id: 'KB_Degradation', score: 0.88, hit: true },
      { page_id: 'RAG_Evaluation', score: 0.72, hit: true },
      { page_id: 'Agentic_RAG', score: 0.58, hit: false },
      { page_id: 'Long_Context', score: 0.45, hit: false },
      { page_id: 'Self_RAG', score: 0.22, hit: false },
    ],
    all_hit: false,
    failure_reasons: [
      'Citation_Faithfulness is an orphan page with no incoming links — not reachable via graph traversal',
      'Missing alias: "knowledge base degradation" does not map to KB_Degradation',
    ],
    suggestions: [
      'Add backlinks to Citation_Faithfulness from RAG and RAG_Evaluation',
      'Add an alias "knowledge base degradation" → KB_Degradation',
    ],
  },
  {
    query_id: 'QRY-003',
    query: 'How does self-corrective retrieval-augmented generation work?',
    expected_pages: ['Self_RAG', 'Corrective_RAG', 'Agentic_RAG'],
    retrieved_pages: [
      { page_id: 'Self_RAG', score: 0.85, hit: true },
      { page_id: 'Agentic_RAG', score: 0.67, hit: true },
      { page_id: 'Corrective_RAG', score: 0.52, hit: true },
      { page_id: 'RAG', score: 0.38, hit: false },
      { page_id: 'RAG_Evaluation', score: 0.19, hit: false },
    ],
    all_hit: true,
    failure_reasons: [],
    suggestions: [],
  },
];


const RAG_CLAIMS: Claim[] = [
  { claim_id: 'CLM-101', text: 'Agent-maintained KBs show measurable degradation after 3+ rounds', page_id: 'KB_Degradation', source_ids: ['SRC-001'], round_created: 3, round_updated: 3, status: 'verified' },
  { claim_id: 'CLM-102', text: 'Orphan pages are the primary cause of retrieval failures', page_id: 'Citation_Faithfulness', source_ids: ['SRC-002'], round_created: 3, round_updated: 3, status: 'unverified' },
  { claim_id: 'CLM-103', text: 'Diagnosis and repair restores 90% of lost retrieval performance', page_id: 'KB_Degradation', source_ids: ['SRC-003'], round_created: 3, round_updated: 3, status: 'verified' },
  { claim_id: 'CLM-201', text: 'Citation faithfulness correlates with retrieval accuracy (r=0.72)', page_id: 'RAG_Evaluation', source_ids: ['SRC-004'], round_created: 3, round_updated: 3, status: 'verified' },
];

// ── API functions ──────────────────────────────────────────────────

export async function getDiagnosisSummary(round_name?: string): Promise<HealthReport[]> {
  if (USE_MOCK) {
    if (round_name) return RAG_HEALTH_REPORTS.filter((r) => r.round_name === round_name);
    return RAG_HEALTH_REPORTS;
  }
  const url = round_name
    ? `/api/diagnosis/summary?round_name=${round_name}`
    : '/api/diagnosis/summary';
  return apiFetch<HealthReport[]>(url);
}

export async function getIssues(round_name?: string): Promise<Issue[]> {
  if (USE_MOCK) return RAG_ISSUES;
  const url = round_name
    ? `/api/diagnosis/issues?round_name=${round_name}`
    : '/api/diagnosis/issues';
  return apiFetch<Issue[]>(url);
}

export async function getKnowledgeGraph(round_name?: string): Promise<LinkGraph> {
  if (USE_MOCK) return { nodes: RAG_NODES, edges: RAG_EDGES };
  const url = round_name
    ? `/api/graph/knowledge?round_name=${round_name}`
    : '/api/graph/knowledge';
  return apiFetch<LinkGraph>(url);
}

export async function getProvenanceGraph(): Promise<LinkGraph> {
  if (USE_MOCK) return { nodes: RAG_NODES.map((n) => ({ ...n, type: 'claim' })), edges: RAG_EDGES.map((e) => ({ ...e, type: 'cites' })) };
  return apiFetch<LinkGraph>('/api/graph/provenance');
}

export async function evaluateRetrieval(round_name?: string): Promise<RetrievalResult[]> {
  if (USE_MOCK) return RAG_RETRIEVAL_RESULTS;
  const url = round_name
    ? `/api/retrieval/evaluate?round_name=${round_name}`
    : '/api/retrieval/evaluate';
  return apiFetch<RetrievalResult[]>(url, { method: 'POST' });
}

export async function getExperimentMetrics(): Promise<HealthReport[]> {
  if (USE_MOCK) return RAG_HEALTH_REPORTS;
  return apiFetch<HealthReport[]>('/api/experiments/metrics');
}

export async function exportExperiment(format: 'csv' | 'json'): Promise<string> {
  if (USE_MOCK) {
    if (format === 'csv') {
      const h = 'round_name,citation_coverage,orphan_rate,duplicate_rate,conflict_density,recall_at_3,mrr';
      const rows = RAG_HEALTH_REPORTS.map((r) =>
        [r.round_name, r.citation_coverage, r.orphan_rate, r.duplicate_rate, r.conflict_density, r.recall_at_3, r.mrr].join(',')
      );
      return [h, ...rows].join('\n');
    }
    return JSON.stringify(RAG_HEALTH_REPORTS, null, 2);
  }
  const res = await fetch(`/api/experiments/export?format=${format}`);
  if (!res.ok) throw new Error(`Export error: ${res.status}`);
  return res.text();
}

export async function askAgent(
  question: string,
  roundName: string,
): Promise<{ answer: string; sources: string[] }> {
  if (USE_MOCK) {
    const low = question.toLowerCase();
    if (low.includes('recall') || low.includes('r@3')) {
      return {
        answer:
          'Recall@3 has dropped from 0.85 (round 1) to 0.55 (round 3) due to increasing orphan pages, duplicate concepts, and broken links. Orphan pages are the primary cause — they have no incoming links and are unreachable via graph traversal. Fix orphan pages first to restore recall.',
        sources: ['diagnosis_metrics', 'knowledge_graph'],
      };
    }
    if (low.includes('issue') || low.includes('top')) {
      return {
        answer:
          'Found 34 issues in round 3 across 5 types: orphan: 11, duplicate: 8, conflict: 5, broken_link: 6, missing_citation: 4. Orphan pages are the most critical as they directly reduce recall. Prioritize fixing orphans and merging duplicates.',
        sources: ['diagnosis_issues'],
      };
    }
    if (low.includes('orphan')) {
      return {
        answer:
          'There are 11 orphan pages — concepts with no incoming links. Key orphans include Citation_Faithfulness and Multimodal_RAG. These pages are unreachable through graph traversal. Fix by adding [[wikilink]] references from related concept pages back to each orphan.',
        sources: ['diagnosis_issues', 'knowledge_graph'],
      };
    }
    if (low.includes('duplicate')) {
      return {
        answer:
          'Found 8 duplicate concept pages. Key overlaps: Self_RAG/Corrective_RAG describe similar self-corrective mechanisms. Duplicates split the retrieval score across multiple pages, reducing ranking precision. Merge into canonical pages.',
        sources: ['diagnosis_issues'],
      };
    }
    if (low.includes('conflict')) {
      return {
        answer:
          'There are 5 conflicting claims, most notably on Long_Context where one claim states LLMs maintain >90% accuracy at 128K tokens while another says accuracy degrades below 60% beyond 32K. Resolve by scoping claims to specific models and benchmarks.',
        sources: ['diagnosis_issues'],
      };
    }
    if (low.includes('health') || low.includes('structure')) {
      return {
        answer:
          'KB structure health has degraded across rounds. Citation coverage dropped from 85% to 62%. Orphan rate rose from 10% to 28%. The knowledge graph has 65 nodes and 56 edges, but 11 nodes are disconnected. Repair round restored recall to 0.78.',
        sources: ['diagnosis_summary', 'knowledge_graph'],
      };
    }
    return {
      answer:
        'The knowledge base currently has 34 detected issues. Key metrics: Recall@3=0.55, Orphan rate=28%, Duplicate rate=25%, Conflict density=0.40. You can ask about specific issue types (orphans, duplicates, conflicts) or retrieval performance.',
      sources: ['diagnosis_summary'],
    };
  }
  const res = await fetch('/api/pipeline/agent/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, round_name: roundName }),
  });
  if (!res.ok) {
    throw new Error(`Agent API error: ${res.status}`);
  }
  return res.json();
}

// ── New experiment endpoints ──────────────────────────────────────

const METHOD_COMPARISON_MOCK: Record<string, MethodComparison> = {
  round_1: {
    round_name: 'round_1',
    methods: [
      { method: 'raw_doc_rag', recall_at_3: 0.60, mrr: 0.52, total_queries: 48, passed_queries: 29, description: 'Direct source document TF-IDF index, no wiki structure' },
      { method: 'static_wiki', recall_at_3: 0.82, mrr: 0.75, total_queries: 48, passed_queries: 39, description: 'Round 1 wiki pages only, frozen (no updates)' },
      { method: 'agent_wiki', recall_at_3: 0.85, mrr: 0.78, total_queries: 48, passed_queries: 41, description: 'Agent-built wiki at current round (no repair)' },
      { method: 'agentkb_diag', recall_at_3: 0.85, mrr: 0.78, total_queries: 48, passed_queries: 41, description: 'Agent-built wiki + diagnosis-driven repair' },
    ],
    queries: [],
  },
  round_2: {
    round_name: 'round_2',
    methods: [
      { method: 'raw_doc_rag', recall_at_3: 0.63, mrr: 0.54, total_queries: 48, passed_queries: 30, description: 'Direct source document TF-IDF index, no wiki structure' },
      { method: 'static_wiki', recall_at_3: 0.82, mrr: 0.75, total_queries: 48, passed_queries: 39, description: 'Round 1 wiki pages only, frozen (no updates)' },
      { method: 'agent_wiki', recall_at_3: 0.72, mrr: 0.65, total_queries: 48, passed_queries: 35, description: 'Agent-built wiki at current round (no repair)' },
      { method: 'agentkb_diag', recall_at_3: 0.80, mrr: 0.73, total_queries: 48, passed_queries: 38, description: 'Agent-built wiki + diagnosis-driven repair' },
    ],
    queries: [],
  },
  round_3: {
    round_name: 'round_3',
    methods: [
      { method: 'raw_doc_rag', recall_at_3: 0.48, mrr: 0.42, total_queries: 48, passed_queries: 23, description: 'Direct source document TF-IDF index, no wiki structure' },
      { method: 'static_wiki', recall_at_3: 0.62, mrr: 0.55, total_queries: 48, passed_queries: 30, description: 'Round 1 wiki pages only, frozen (no updates)' },
      { method: 'agent_wiki', recall_at_3: 0.55, mrr: 0.48, total_queries: 48, passed_queries: 26, description: 'Agent-built wiki at current round (no repair)' },
      { method: 'agentkb_diag', recall_at_3: 0.78, mrr: 0.72, total_queries: 48, passed_queries: 37, description: 'Agent-built wiki + diagnosis-driven repair' },
    ],
    queries: [],
  },
  repair: {
    round_name: 'repair',
    methods: [
      { method: 'raw_doc_rag', recall_at_3: 0.48, mrr: 0.42, total_queries: 48, passed_queries: 23, description: 'Direct source document TF-IDF index, no wiki structure' },
      { method: 'static_wiki', recall_at_3: 0.62, mrr: 0.55, total_queries: 48, passed_queries: 30, description: 'Round 1 wiki pages only, frozen (no updates)' },
      { method: 'agent_wiki', recall_at_3: 0.55, mrr: 0.48, total_queries: 48, passed_queries: 26, description: 'Agent-built wiki at current round (no repair)' },
      { method: 'agentkb_diag', recall_at_3: 0.78, mrr: 0.72, total_queries: 48, passed_queries: 37, description: 'Agent-built wiki + diagnosis-driven repair' },
    ],
    queries: [],
  },
};

const CASE_STUDIES_MOCK: CaseStudy[] = [
  {
    case_id: 'case_001',
    title: 'Case 1: Duplicate Concepts Fragment Retrieval Signal',
    phenomenon: '在第三轮维护后，Self_RAG与Corrective_RAG分别描述了自反思式检索增强生成方法，但二者始终保持为独立页面...',
    diagnosis: 'AgentKB-Diag检测到重复率从0.10上升至0.25，Self_RAG与Corrective_RAG概念相似度0.73...',
    repair: '合并Self_RAG和Corrective_RAG为统一页面，添加别名映射，更新Wikilink引用...',
    before_metric: 0.55,
    after_metric: 0.78,
    relevant_pages: ['Self_RAG', 'Corrective_RAG'],
    relevant_query_ids: ['q_042', 'q_047', 'q_015', 'q_032'],
  },
  {
    case_id: 'case_002',
    title: 'Case 2: Orphan Concept Becomes Undiscoverable',
    phenomenon: 'Citation_Faithfulness页面在第三轮创建后没有任何入链，成为知识图谱中的孤立节点...',
    diagnosis: 'AgentKB-Diag孤岛检测发现Citation_Faithfulness入度为0，相关查询的检索排名跌至第8位之后...',
    repair: '添加来自RAG_Evaluation和RAG的入链，补充中英文别名，恢复检索可达性...',
    before_metric: 0.55,
    after_metric: 0.78,
    relevant_pages: ['Citation_Faithfulness', 'RAG_Evaluation', 'RAG'],
    relevant_query_ids: ['q_008', 'q_046', 'q_041'],
  },
  {
    case_id: 'case_003',
    title: 'Case 3: Unsupported Claims Undermine Trust',
    phenomenon: 'GraphRAG的claim_011声称有15-25%性能提升但无来源引用，进而衍生出KG_RAG的虚假30%声明...',
    diagnosis: '来源追溯显示claim_011的出处链路完全断裂，形成了unsupported claim cascade...',
    repair: '补充基准测试引用来源，修正过度推广的数值声明，添加上下文限定...',
    before_metric: 0.55,
    after_metric: 0.78,
    relevant_pages: ['GraphRAG', 'KG_RAG', 'Long_Context'],
    relevant_query_ids: ['q_003', 'q_011', 'q_045'],
  },
  {
    case_id: 'case_004',
    title: 'Case 4: Repair Restores Retrieval Performance',
    phenomenon: '三轮维护后Recall@3从0.85降至0.55，孤岛率从0.10升至0.28，重复率从0.05升至0.25...',
    diagnosis: 'AgentKB-Diag检测34个问题：11孤岛、8重复、5冲突、6断链、4缺来源...',
    repair: '系统性修复：合并4组重复、添加7个孤岛入链、补充16条别名、补充12个来源...',
    before_metric: 0.55,
    after_metric: 0.78,
    relevant_pages: ['Self_RAG', 'Corrective_RAG', 'Citation_Faithfulness', 'GraphRAG', 'KB_Degradation'],
    relevant_query_ids: ['q_041', 'q_042', 'q_044', 'q_046', 'q_048'],
  },
];


export async function getMethodComparison(roundName: string): Promise<MethodComparison> {
  if (USE_MOCK) {
    return METHOD_COMPARISON_MOCK[roundName] || METHOD_COMPARISON_MOCK.round_3;
  }
  return apiFetch<MethodComparison>(`/api/experiments/method-comparison?round_name=${roundName}`);
}

export async function getCaseStudies(): Promise<CaseStudy[]> {
  if (USE_MOCK) return CASE_STUDIES_MOCK;
  return apiFetch<CaseStudy[]>('/api/experiments/cases');
}

// Legacy aliases for backward compatibility
export async function runDiagnosis(): Promise<{ status: string }> {
  if (USE_MOCK) return { status: 'completed' };
  return apiFetch<{ status: string }>('/api/diagnosis/run', { method: 'POST' });
}
