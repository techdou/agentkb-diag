import React from 'react';
import KnowledgeGraph from '../structure/KnowledgeGraph';
import IssueFilter from '../structure/IssueFilter';
import { getProvenanceGraph } from '../../utils/api';
import type { LinkGraph } from '../../types';

export default function ProvenancePage() {
  const [graph, setGraph] = React.useState<LinkGraph | null>(null);
  const [filter, setFilter] = React.useState('all');
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    setLoading(true);
    getProvenanceGraph()
      .then(setGraph)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height: '100%', color: 'var(--color-text-secondary)' }}>
        Loading provenance graph...
      </div>
    );
  }

  if (!graph) {
    return (
      <div className="flex items-center justify-center" style={{ height: '100%', color: 'var(--color-text-secondary)' }}>
        No provenance data available.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-card)' }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 4 }}>
          Claim-Source Provenance Graph
        </div>
        <div style={{ fontSize: 13, color: 'var(--color-text)', lineHeight: 1.5 }}>
          This graph shows the citation relationships between claims and their supporting sources across wiki rounds.
          Select a node to inspect its provenance trail.
        </div>
      </div>
      <IssueFilter value={filter} onChange={setFilter} />
      <KnowledgeGraph graph={graph} filter={filter} />
    </div>
  );
}
