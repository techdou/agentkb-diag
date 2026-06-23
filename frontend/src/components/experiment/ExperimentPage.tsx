import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {
  getExperimentMetrics,
  exportExperiment,
  getMethodComparison,
  getCaseStudies,
} from '../../utils/api';
import type { HealthReport, MethodComparison, MethodResult, CaseStudy } from '../../types';

const ROUND_LABELS: Record<string, string> = {
  round_1: 'Round 1',
  round_2: 'Round 2',
  round_3: 'Round 3',
  repair: 'Repair',
};

const METRIC_KEYS = [
  'citation_coverage',
  'orphan_rate',
  'duplicate_rate',
  'conflict_density',
  'recall_at_3',
  'mrr',
] as const;

const METRIC_LABELS: Record<string, string> = {
  citation_coverage: 'Citation Coverage',
  orphan_rate: 'Orphan Rate',
  duplicate_rate: 'Duplicate Rate',
  conflict_density: 'Conflict Density',
  recall_at_3: 'Recall@3',
  mrr: 'MRR',
};

const METHOD_LABELS: Record<string, string> = {
  raw_doc_rag: 'Raw-doc RAG',
  static_wiki: 'Static Wiki-RAG',
  agent_wiki: 'Agent Wiki-RAG',
  agentkb_diag: 'AgentKB-Diag',
};

function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ExperimentPage() {
  const [reports, setReports] = React.useState<HealthReport[]>([]);
  const [methodComp, setMethodComp] = React.useState<MethodComparison | null>(null);
  const [cases, setCases] = React.useState<CaseStudy[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [exporting, setExporting] = React.useState(false);
  const [expandedCase, setExpandedCase] = React.useState<string | null>(null);

  React.useEffect(() => {
    setLoading(true);
    Promise.all([
      getExperimentMetrics(),
      getMethodComparison('round_3'),
      getCaseStudies(),
    ])
      .then(([repData, mcData, csData]) => {
        setReports(Array.isArray(repData) ? repData : []);
        setMethodComp(mcData);
        setCases(Array.isArray(csData) ? csData : []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleExport = async (format: 'csv' | 'json') => {
    setExporting(true);
    try {
      const content = await exportExperiment(format);
      const ext = format === 'csv' ? 'csv' : 'json';
      const mime = format === 'csv' ? 'text/csv' : 'application/json';
      downloadBlob(content, `experiment_results.${ext}`, mime);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        Loading experiment data...
      </div>
    );
  }

  // Build comparison data for R3 vs Repair bar chart
  const r3 = reports.find((r) => r.round_name === 'round_3');
  const repair = reports.find((r) => r.round_name === 'repair');
  const comparisonData = r3 && repair
    ? METRIC_KEYS.map((key) => ({
        metric: METRIC_LABELS[key],
        'Round 3 (Degraded)': r3[key],
        'After Repair': repair[key],
      }))
    : [];

  // Build method comparison bar chart data
  const methodChartData = methodComp?.methods.map((m) => ({
    method: METHOD_LABELS[m.method] || m.method,
    Recall3: m.recall_at_3,
    MRR: m.mrr,
  })) || [];

  // Compute statistical note
  const rawDoc = methodComp?.methods.find((m) => m.method === 'raw_doc_rag');
  const diag = methodComp?.methods.find((m) => m.method === 'agentkb_diag');
  const delta = rawDoc && diag ? diag.recall_at_3 - rawDoc.recall_at_3 : 0;
  const deltaPct = rawDoc && rawDoc.recall_at_3 > 0 ? ((delta / rawDoc.recall_at_3) * 100).toFixed(1) : '0.0';

  return (
    <div style={{ padding: 0, maxWidth: 960 }}>
      {/* ── Section 1: Method Comparison Table ────────────────── */}
      <div className="panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
          <div className="panel-title" style={{ marginBottom: 0 }}>Method Comparison</div>
          <div style={{ display: 'flex', gap: 6 }}>
            <button className="topbar-btn" onClick={() => handleExport('csv')} disabled={exporting}>
              {exporting ? '...' : 'CSV'}
            </button>
            <button className="topbar-btn" onClick={() => handleExport('json')} disabled={exporting}>
              {exporting ? '...' : 'JSON'}
            </button>
          </div>
        </div>

        {methodComp && (
          <>
            <table className="compact-table" style={{ marginBottom: 10 }}>
              <thead>
                <tr>
                  <th>Method</th>
                  <th>Recall@3</th>
                  <th>MRR</th>
                  <th>Passed</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {methodComp.methods.map((m) => (
                  <tr key={m.method} style={m.method === 'agentkb_diag' ? { background: 'rgba(22, 163, 74, 0.06)' } : undefined}>
                    <td style={{ fontWeight: 600 }}>{METHOD_LABELS[m.method] || m.method}</td>
                    <td>{m.recall_at_3.toFixed(2)}</td>
                    <td>{m.mrr.toFixed(2)}</td>
                    <td>{m.passed_queries}/{m.total_queries}</td>
                    <td style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{m.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Statistical note */}
            <div style={{
              fontSize: 11,
              color: 'var(--text-secondary)',
              padding: '6px 10px',
              background: 'var(--bg-secondary, #f8fafc)',
              borderRadius: 4,
              borderLeft: '3px solid var(--accent, #2563eb)',
            }}>
              Diag vs Raw-doc: +{delta.toFixed(2)} R@3 (Δ={deltaPct}%). &nbsp;
              Diag vs Agent-wiki: +{diag && methodComp.methods.find((m) => m.method === 'agent_wiki') ? (diag.recall_at_3 - (methodComp.methods.find((m) => m.method === 'agent_wiki')?.recall_at_3 || 0)).toFixed(2) : '0.00'} R@3.
              Repair restores retrieval to near Round 1 levels.
            </div>

            {/* Method comparison bar chart */}
            <div style={{ marginTop: 14 }}>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={methodChartData} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="method" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} domain={[0, 1]} />
                  <Tooltip contentStyle={{ fontSize: 11, borderRadius: 4, border: '1px solid var(--border)' }} />
                  <Bar dataKey="Recall3" fill="#2563eb" radius={[2, 2, 0, 0]} name="Recall@3" />
                  <Bar dataKey="MRR" fill="#94a3b8" radius={[2, 2, 0, 0]} name="MRR" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
        {!methodComp && (
          <div style={{ color: 'var(--text-secondary)', fontSize: 13, padding: 8 }}>
            Method comparison data unavailable. Run a round to generate results.
          </div>
        )}
      </div>

      {/* ── Section 2: Round Evolution Table ──────────────────── */}
      <div className="panel">
        <div className="panel-title">Round Evolution</div>

        <table className="compact-table">
          <thead>
            <tr>
              <th>Round</th>
              {METRIC_KEYS.map((key) => (
                <th key={key}>{METRIC_LABELS[key]}</th>
              ))}
              <th>Pages</th>
              <th>Claims</th>
              <th>Issues</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.round_name}>
                <td style={{ fontWeight: 600 }}>{ROUND_LABELS[r.round_name] || r.round_name}</td>
                {METRIC_KEYS.map((key) => (
                  <td key={key}>{r[key].toFixed(2)}</td>
                ))}
                <td>{r.page_count}</td>
                <td>{r.claim_count}</td>
                <td>{r.issue_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── Section 3: R3 vs Repair comparison bar chart ──────── */}
      {comparisonData.length > 0 && (
        <div className="panel">
          <div className="panel-title">Round 3 vs Repair Comparison</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={comparisonData} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="metric" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ fontSize: 11, borderRadius: 4, border: '1px solid var(--border)' }}
              />
              <Bar dataKey="Round 3 (Degraded)" fill="#ef4444" radius={[2, 2, 0, 0]} />
              <Bar dataKey="After Repair" fill="#16a34a" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* ── Section 4: Case Studies ───────────────────────────── */}
      <div className="panel">
        <div className="panel-title">Case Studies</div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 10 }}>
          4 paper-level case studies demonstrating the degradation-diagnosis-repair-recovery cycle.
        </div>

        {cases.map((c) => {
          const isExpanded = expandedCase === c.case_id;
          const improvement = c.after_metric - c.before_metric;
          const improvementPct = ((improvement / c.before_metric) * 100).toFixed(1);

          return (
            <div
              key={c.case_id}
              style={{
                border: '1px solid var(--border)',
                borderRadius: 6,
                marginBottom: 10,
                overflow: 'hidden',
              }}
            >
              {/* Header — always visible */}
              <button
                onClick={() => setExpandedCase(isExpanded ? null : c.case_id)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  padding: '10px 14px',
                  border: 'none',
                  background: isExpanded ? 'var(--bg-secondary, #f8fafc)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: 10,
                  fontFamily: 'inherit',
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{c.title}</div>
                  <div style={{ display: 'flex', gap: 14, fontSize: 11, color: 'var(--text-secondary)' }}>
                    <span>
                      Recall@3: {c.before_metric.toFixed(2)} → {c.after_metric.toFixed(2)}
                    </span>
                    <span style={{ color: '#16a34a' }}>
                      +{improvement.toFixed(2)} (+{improvementPct}%)
                    </span>
                    <span>Pages: {c.relevant_pages.join(', ')}</span>
                  </div>
                </div>
                <span style={{
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  transform: isExpanded ? 'rotate(180deg)' : 'none',
                  transition: 'transform 0.15s',
                  marginTop: 2,
                }}>
                  ▼
                </span>
              </button>

              {/* Expanded content */}
              {isExpanded && (
                <div style={{ padding: '0 14px 14px 14px' }}>
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, color: '#ef4444' }}>
                      Phenomenon
                    </div>
                    <div style={{ fontSize: 12, lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                      {c.phenomenon}
                    </div>
                  </div>

                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, color: '#2563eb' }}>
                      Diagnosis
                    </div>
                    <div style={{ fontSize: 12, lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                      {c.diagnosis}
                    </div>
                  </div>

                  <div style={{ marginBottom: 8 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4, color: '#16a34a' }}>
                      Repair
                    </div>
                    <div style={{ fontSize: 12, lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                      {c.repair}
                    </div>
                  </div>

                  <div style={{
                    display: 'flex',
                    gap: 20,
                    fontSize: 11,
                    color: 'var(--text-secondary)',
                    marginTop: 10,
                    paddingTop: 8,
                    borderTop: '1px solid var(--border)',
                  }}>
                    <span>
                      <strong>Queries:</strong> {c.relevant_query_ids.join(', ')}
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
