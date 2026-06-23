import React from 'react';
import { useAppState } from '../../store/appStore';
import { evaluateRetrieval } from '../../utils/api';
import type { RetrievalResult, SearchResult } from '../../types';

export default function FailurePage() {
  const { selectedRound } = useAppState();
  const [results, setResults] = React.useState<RetrievalResult[]>([]);
  const [selectedQueryId, setSelectedQueryId] = React.useState<string>('');
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    setLoading(true);
    setSelectedQueryId('');
    evaluateRetrieval(selectedRound)
      .then((data) => {
        setResults(Array.isArray(data) ? data : []);
        if (data.length > 0) setSelectedQueryId(data[0].query_id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedRound]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        Loading retrieval analysis...
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        No retrieval data available.
      </div>
    );
  }

  const selected = results.find((r) => r.query_id === selectedQueryId) || results[0];

  return (
    <div className="failure-layout" style={{ padding: 0, height: 'calc(100vh - 76px)' }}>
      {/* Query Panel (22%) */}
      <div className="panel failure-col query" style={{ marginBottom: 0 }}>
        <div className="panel-title">Queries</div>
        <select
          value={selectedQueryId}
          onChange={(e) => setSelectedQueryId(e.target.value)}
          style={{
            width: '100%',
            padding: '4px 6px',
            border: '1px solid var(--border)',
            borderRadius: 4,
            fontSize: 11,
            marginBottom: 10,
          }}
        >
          {results.map((r) => (
            <option key={r.query_id} value={r.query_id}>
              {r.query_id}
            </option>
          ))}
        </select>

        <div style={{ fontSize: 12, lineHeight: 1.5, marginBottom: 10, color: 'var(--text)' }}>
          {selected.query}
        </div>

        <div style={{ fontSize: 10.5, color: 'var(--text-secondary)', marginBottom: 6 }}>
          Expected Pages
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 8 }}>
          {selected.expected_pages.map((p) => (
            <span key={p} className="issue-badge missing_citation">{p}</span>
          ))}
        </div>

        <div style={{ fontSize: 10.5, color: 'var(--text-secondary)', marginBottom: 4 }}>
          Status: {' '}
          <span style={{ fontWeight: 600, color: selected.all_hit ? '#16a34a' : 'var(--orphan)' }}>
            {selected.all_hit ? 'ALL HIT' : 'MISS'}
          </span>
        </div>
      </div>

      {/* Results Panel (50%) */}
      <div className="panel failure-col results" style={{ marginBottom: 0 }}>
        <div className="panel-title">Retrieved Pages</div>
        <table className="compact-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Page</th>
              <th>Score</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {selected.retrieved_pages.map((r: SearchResult, i: number) => (
              <tr key={r.page_id}>
                <td style={{ color: 'var(--text-muted)', width: 28 }}>{i + 1}</td>
                <td>{r.page_id}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 64, height: 5, backgroundColor: '#e2e8f0', borderRadius: 3, overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          borderRadius: 3,
                          backgroundColor: r.hit ? '#16a34a' : '#3b82f6',
                          width: `${(r.score * 100).toFixed(0)}%`,
                        }}
                      />
                    </div>
                    <span style={{ fontSize: 10.5, fontVariantNumeric: 'tabular-nums' }}>
                      {r.score.toFixed(2)}
                    </span>
                  </div>
                </td>
                <td>
                  <span className={`issue-badge ${r.hit ? 'missing_citation' : 'orphan'}`}>
                    {r.hit ? 'HIT' : 'MISS'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Attribution Panel (28%) */}
      <div className="panel failure-col attribution" style={{ marginBottom: 0 }}>
        <div className="panel-title">Failure Attribution</div>
        {selected.all_hit ? (
          <div style={{ fontSize: 12, color: '#16a34a' }}>
            All expected pages were retrieved successfully.
          </div>
        ) : (
          <>
            {selected.failure_reasons && selected.failure_reasons.length > 0 && (
              <div style={{ marginBottom: 10 }}>
                <div style={{ fontWeight: 600, fontSize: 11, marginBottom: 4, color: 'var(--orphan)' }}>
                  Reasons
                </div>
                {selected.failure_reasons.map((reason, i) => (
                  <div
                    key={i}
                    style={{
                      fontSize: 11,
                      marginBottom: 5,
                      paddingLeft: 8,
                      borderLeft: '2px solid var(--orphan)',
                      lineHeight: 1.4,
                    }}
                  >
                    {reason}
                  </div>
                ))}
              </div>
            )}

            {selected.suggestions && selected.suggestions.length > 0 && (
              <div>
                <div style={{ fontWeight: 600, fontSize: 11, marginBottom: 4, color: 'var(--accent)' }}>
                  Fix Suggestions
                </div>
                {selected.suggestions.map((sug, i) => (
                  <div
                    key={i}
                    style={{
                      fontSize: 11,
                      marginBottom: 4,
                      paddingLeft: 8,
                      borderLeft: '2px solid var(--accent)',
                      lineHeight: 1.4,
                      color: 'var(--text-secondary)',
                    }}
                  >
                    {sug}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
