import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useAppState } from '../../store/appStore';
import { getExperimentMetrics, getIssues } from '../../utils/api';
import type { HealthReport, Issue } from '../../types';

const METRIC_COLORS: Record<string, string> = {
  citation_coverage: '#3b82f6',
  orphan_rate: '#ef4444',
  duplicate_rate: '#f97316',
  conflict_density: '#a855f7',
  recall_at_3: '#16a34a',
  mrr: '#0891b2',
};

const METRIC_LABELS: Record<string, string> = {
  citation_coverage: 'Citation Coverage',
  orphan_rate: 'Orphan Rate',
  duplicate_rate: 'Duplicate Rate',
  conflict_density: 'Conflict Density',
  recall_at_3: 'Recall@3',
  mrr: 'MRR',
};

const ROUND_LABELS: Record<string, string> = {
  round_1: 'R1',
  round_2: 'R2',
  round_3: 'R3',
  repair: 'Repair',
};

const ISSUE_TYPE_COLORS: Record<string, string> = {
  orphan: '#ef4444',
  duplicate: '#f97316',
  conflict: '#a855f7',
  broken_link: '#eab308',
  missing_citation: '#0891b2',
};

const ISSUE_TYPE_LABELS: Record<string, string> = {
  orphan: 'Orphan',
  duplicate: 'Duplicate',
  conflict: 'Conflict',
  broken_link: 'Broken Link',
  missing_citation: 'Missing Citation',
};

function formatMetricValue(key: string, value: number): string {
  if (key === 'mrr') return value.toFixed(3);
  return (value * 100).toFixed(1) + '%';
}

export default function OverviewPage() {
  const { selectedRound } = useAppState();
  const [reports, setReports] = React.useState<HealthReport[]>([]);
  const [issues, setIssues] = React.useState<Issue[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    setLoading(true);
    Promise.all([getExperimentMetrics(), getIssues(selectedRound)])
      .then(([r, i]) => {
        setReports(Array.isArray(r) ? r : []);
        setIssues(Array.isArray(i) ? i : []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedRound]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        Loading...
      </div>
    );
  }

  // Prepare chart data: one row per round
  const chartData = reports.map((r) => ({
    round: ROUND_LABELS[r.round_name] || r.round_name,
    citation_coverage: r.citation_coverage,
    orphan_rate: r.orphan_rate,
    duplicate_rate: r.duplicate_rate,
    conflict_density: r.conflict_density,
    recall_at_3: r.recall_at_3,
    mrr: r.mrr,
  }));

  // Issue type distribution counts
  const issueCounts: Record<string, number> = {};
  for (const iss of issues) {
    issueCounts[iss.type] = (issueCounts[iss.type] || 0) + 1;
  }
  const totalIssues = issues.length;
  const issueTypes = Object.keys(issueCounts).sort(
    (a, b) => issueCounts[b] - issueCounts[a]
  );

  return (
    <div>
      {/* Health Evolution Chart */}
      <div className="panel">
        <div className="panel-title">Knowledge Health Evolution</div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="round" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 10 }} domain={[0, 1]} tickFormatter={(v: number) => (v * 100).toFixed(0) + '%'} />
            <Tooltip
              contentStyle={{ fontSize: 11, borderRadius: 4, border: '1px solid var(--border)' }}
              formatter={(value: number, name: string) => [formatMetricValue(name, value), METRIC_LABELS[name] || name]}
            />
            <Legend
              wrapperStyle={{ fontSize: 10.5, paddingTop: 4 }}
              formatter={(value: string) => METRIC_LABELS[value] || value}
            />
            {Object.keys(METRIC_COLORS).map((key) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={METRIC_COLORS[key]}
                strokeWidth={1.5}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Middle row: Key Findings + Metrics Table */}
      <div className="grid-2">
        {/* Key Findings */}
        <div className="panel">
          <div className="panel-title">Key Findings</div>
          {issues.length === 0 ? (
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>No issues detected for this round.</div>
          ) : (
            <div style={{ fontSize: 12, lineHeight: 1.6 }}>
              {issues.slice(0, 8).map((iss) => (
                <div key={iss.issue_id} style={{ marginBottom: 6, paddingLeft: 10, borderLeft: `2px solid ${ISSUE_TYPE_COLORS[iss.type] || '#94a3b8'}` }}>
                  <span style={{ fontWeight: 600, color: ISSUE_TYPE_COLORS[iss.type] }}>
                    [{iss.type.toUpperCase()}]
                  </span>{' '}
                  {iss.description}
                </div>
              ))}
              {issues.length > 8 && (
                <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                  +{issues.length - 8} more issues
                </div>
              )}
            </div>
          )}
        </div>

        {/* Metrics Table */}
        <div className="panel">
          <div className="panel-title">Round Metrics</div>
          <table className="compact-table">
            <thead>
              <tr>
                <th>Round</th>
                <th>CC</th>
                <th>Orph</th>
                <th>Dup</th>
                <th>Cfl</th>
                <th>R@3</th>
                <th>MRR</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.round_name}>
                  <td style={{ fontWeight: 600 }}>{ROUND_LABELS[r.round_name] || r.round_name}</td>
                  <td>{r.citation_coverage.toFixed(2)}</td>
                  <td>{r.orphan_rate.toFixed(2)}</td>
                  <td>{r.duplicate_rate.toFixed(2)}</td>
                  <td>{r.conflict_density.toFixed(2)}</td>
                  <td>{r.recall_at_3.toFixed(2)}</td>
                  <td>{r.mrr.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Issue Distribution Bar */}
      <div className="panel">
        <div className="panel-title">
          Issue Distribution ({totalIssues} total in {ROUND_LABELS[selectedRound] || selectedRound})
        </div>
        {totalIssues === 0 ? (
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>No issues.</div>
        ) : (
          <div>
            <div style={{ display: 'flex', height: 20, borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              {issueTypes.map((type) => {
                const pct = (issueCounts[type] / totalIssues) * 100;
                return (
                  <div
                    key={type}
                    style={{
                      width: `${pct}%`,
                      backgroundColor: ISSUE_TYPE_COLORS[type] || '#94a3b8',
                      minWidth: pct > 0 ? 2 : 0,
                    }}
                    title={`${ISSUE_TYPE_LABELS[type]}: ${issueCounts[type]}`}
                  />
                );
              })}
            </div>
            <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', fontSize: 11 }}>
              {issueTypes.map((type) => (
                <span key={type} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span
                    style={{
                      display: 'inline-block',
                      width: 8,
                      height: 8,
                      borderRadius: 2,
                      backgroundColor: ISSUE_TYPE_COLORS[type] || '#94a3b8',
                    }}
                  />
                  {ISSUE_TYPE_LABELS[type]}: {issueCounts[type]}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
