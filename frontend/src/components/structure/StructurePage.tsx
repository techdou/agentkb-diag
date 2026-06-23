import React from 'react';
import { useAppState } from '../../store/appStore';
import { getKnowledgeGraph } from '../../utils/api';
import type { GraphNode, GraphEdge, LinkGraph } from '../../types';

interface NodePos {
  x: number;
  y: number;
}

const FILTER_OPTIONS = ['all', 'orphan', 'duplicate', 'conflict'] as const;
type FilterType = (typeof FILTER_OPTIONS)[number];

const ISSUE_STROKE: Record<string, string> = {
  orphan: '#ef4444',
  duplicate: '#f97316',
  conflict: '#a855f7',
};

const ISSUE_LABELS: Record<string, string> = {
  orphan: 'Orphan',
  duplicate: 'Duplicate',
  conflict: 'Conflict',
  broken_link: 'Broken Link',
  missing_citation: 'Missing Citation',
};

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + '\u2026' : s;
}

function hasIssue(node: GraphNode, type: FilterType): boolean {
  if (type === 'all') return true;
  return node.issue_flags.includes(type);
}

function getIssueStroke(node: GraphNode): string | undefined {
  for (const flag of node.issue_flags) {
    if (ISSUE_STROKE[flag]) return ISSUE_STROKE[flag];
  }
  return undefined;
}

function runForceSim(
  nodes: GraphNode[],
  edges: GraphEdge[],
  width: number,
  height: number,
  iterations: number = 50
): Map<string, NodePos> {
  const positions = new Map<string, NodePos>();
  const cx = width / 2;
  const cy = height / 2;

  // Initialize random positions near center
  for (const node of nodes) {
    positions.set(node.id, {
      x: cx + (Math.random() - 0.5) * width * 0.4,
      y: cy + (Math.random() - 0.5) * height * 0.4,
    });
  }

  // Build adjacency for edge degree
  const degree = new Map<string, number>();
  for (const node of nodes) degree.set(node.id, 0);
  for (const edge of edges) {
    degree.set(edge.source, (degree.get(edge.source) || 0) + 1);
    degree.set(edge.target, (degree.get(edge.target) || 0) + 1);
  }

  for (let iter = 0; iter < iterations; iter++) {
    const forces = new Map<string, { fx: number; fy: number }>();
    for (const node of nodes) {
      forces.set(node.id, { fx: 0, fy: 0 });
    }

    // Repulsion between all pairs
    const nodeList = nodes;
    for (let i = 0; i < nodeList.length; i++) {
      const a = nodeList[i];
      const pa = positions.get(a.id)!;
      for (let j = i + 1; j < nodeList.length; j++) {
        const b = nodeList[j];
        const pb = positions.get(b.id)!;
        let dx = pa.x - pb.x;
        let dy = pa.y - pb.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const repulsion = 800 / (dist * dist);
        const fx = (dx / dist) * repulsion;
        const fy = (dy / dist) * repulsion;
        forces.get(a.id)!.fx += fx;
        forces.get(a.id)!.fy += fy;
        forces.get(b.id)!.fx -= fx;
        forces.get(b.id)!.fy -= fy;
      }
    }

    // Attraction along edges (spring)
    for (const edge of edges) {
      const pa = positions.get(edge.source);
      const pb = positions.get(edge.target);
      if (!pa || !pb) continue;
      const dx = pb.x - pa.x;
      const dy = pb.y - pa.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const targetDist = 120;
      const attraction = (dist - targetDist) * 0.01;
      const fx = (dx / dist) * attraction;
      const fy = (dy / dist) * attraction;
      forces.get(edge.source)!.fx += fx;
      forces.get(edge.source)!.fy += fy;
      forces.get(edge.target)!.fx -= fx;
      forces.get(edge.target)!.fy -= fy;
    }

    // Center gravity
    for (const node of nodes) {
      const p = positions.get(node.id)!;
      const gx = (cx - p.x) * 0.005;
      const gy = (cy - p.y) * 0.005;
      forces.get(node.id)!.fx += gx;
      forces.get(node.id)!.fy += gy;
    }

    // Cooling factor
    const cooling = Math.max(0.02, 1 - iter / iterations);
    const maxStep = 30 * cooling;

    // Apply forces
    for (const node of nodes) {
      const p = positions.get(node.id)!;
      const f = forces.get(node.id)!;
      let step = Math.sqrt(f.fx * f.fx + f.fy * f.fy);
      if (step > maxStep) {
        f.fx = (f.fx / step) * maxStep;
        f.fy = (f.fy / step) * maxStep;
      }
      p.x = Math.max(30, Math.min(width - 30, p.x + f.fx));
      p.y = Math.max(30, Math.min(height - 30, p.y + f.fy));
    }
  }

  return positions;
}

export default function StructurePage() {
  const { selectedRound } = useAppState();
  const [graph, setGraph] = React.useState<LinkGraph | null>(null);
  const [filter, setFilter] = React.useState<FilterType>('all');
  const [loading, setLoading] = React.useState(true);
  const [selectedNode, setSelectedNode] = React.useState<GraphNode | null>(null);
  const [tooltip, setTooltip] = React.useState<{ text: string; x: number; y: number } | null>(null);
  const [positions, setPositions] = React.useState<Map<string, NodePos>>(new Map());
  const [svgSize, setSvgSize] = React.useState({ w: 700, h: 500 });
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    setLoading(true);
    setSelectedNode(null);
    getKnowledgeGraph(selectedRound)
      .then((g) => setGraph(g))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedRound]);

  // Run force simulation when graph or container size changes
  React.useEffect(() => {
    if (!graph || graph.nodes.length === 0) return;
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const w = Math.max(500, rect.width - 250); // reserve for detail panel
    const h = Math.max(400, rect.height - 30);
    setSvgSize({ w, h });
    const pos = runForceSim(graph.nodes, graph.edges, w, h, 50);
    setPositions(pos);
  }, [graph]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        Loading graph...
      </div>
    );
  }

  if (!graph || graph.nodes.length === 0) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        No graph data available.
      </div>
    );
  }

  // Filter nodes
  const filteredNodes = graph.nodes.filter((n) => hasIssue(n, filter));
  const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));
  const filteredEdges = graph.edges.filter(
    (e) => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target)
  );

  // Edge count per node for radius
  const edgeCount = new Map<string, number>();
  for (const n of graph.nodes) edgeCount.set(n.id, 0);
  for (const e of graph.edges) {
    edgeCount.set(e.source, (edgeCount.get(e.source) || 0) + 1);
    edgeCount.set(e.target, (edgeCount.get(e.target) || 0) + 1);
  }

  const getRadius = (nodeId: string) => Math.min(16, Math.max(8, 6 + (edgeCount.get(nodeId) || 0) * 1.2));

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
  };

  const handleNodeHover = (
    e: React.MouseEvent,
    node: GraphNode
  ) => {
    if (node.issue_flags.length > 0) {
      setTooltip({
        text: node.issue_flags.map((f) => ISSUE_LABELS[f] || f).join(', '),
        x: e.nativeEvent.offsetX + 12,
        y: e.nativeEvent.offsetY - 8,
      });
    }
  };

  const detailNode = selectedNode
    ? graph.nodes.find((n) => n.id === selectedNode.id) ?? null
    : null;

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      {/* Graph area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Filter bar */}
        <div className="filter-bar" style={{ padding: '8px 12px', marginBottom: 0 }}>
          {FILTER_OPTIONS.map((opt) => (
            <button
              key={opt}
              className={`filter-pill${filter === opt ? ' active' : ''}`}
              onClick={() => setFilter(opt)}
            >
              {opt === 'all' ? 'All' : ISSUE_LABELS[opt]}
            </button>
          ))}
        </div>

        {/* SVG */}
        <div
          ref={containerRef}
          style={{ flex: 1, position: 'relative', overflow: 'hidden' }}
        >
          <svg
            className="graph-svg"
            viewBox={`0 0 ${svgSize.w} ${svgSize.h}`}
            preserveAspectRatio="xMidYMid meet"
          >
            {/* Edges */}
            {filteredEdges.map((e, i) => {
              const sp = positions.get(e.source);
              const tp = positions.get(e.target);
              if (!sp || !tp) return null;
              return (
                <line
                  key={`e-${i}`}
                  className="graph-edge"
                  x1={sp.x}
                  y1={sp.y}
                  x2={tp.x}
                  y2={tp.y}
                />
              );
            })}

            {/* Nodes */}
            {filteredNodes.map((node) => {
              const p = positions.get(node.id);
              if (!p) return null;
              const r = getRadius(node.id);
              const stroke = getIssueStroke(node);
              const isSelected = selectedNode?.id === node.id;
              return (
                <g
                  key={node.id}
                  className="graph-node"
                  onClick={() => handleNodeClick(node)}
                  onMouseEnter={(e) => handleNodeHover(e, node)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  <circle
                    cx={p.x}
                    cy={p.y}
                    r={r}
                    fill={isSelected ? '#3b82f6' : '#cbd5e1'}
                    stroke={isSelected ? '#1d4ed8' : stroke || '#94a3b8'}
                    strokeWidth={stroke ? 2 : 1}
                    opacity={isSelected ? 1 : 0.85}
                  />
                  <text
                    x={p.x}
                    y={p.y + r + 11}
                    textAnchor="middle"
                    fontSize={9}
                    fill={isSelected ? '#1d4ed8' : 'var(--text)'}
                    fontWeight={isSelected ? 600 : 400}
                  >
                    {truncate(node.label, 16)}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Tooltip */}
          {tooltip && (
            <div
              className="tooltip"
              style={{ left: tooltip.x, top: tooltip.y }}
            >
              {tooltip.text}
            </div>
          )}
        </div>
      </div>

      {/* Detail Panel */}
      {detailNode && (
        <div className="detail-panel">
          <div className="detail-title">{detailNode.label}</div>
          <div className="detail-row">ID: {detailNode.id}</div>
          <div className="detail-row">Created: Round {detailNode.round_created}</div>
          <div className="detail-row">
            Edges: {edgeCount.get(detailNode.id) || 0}
          </div>

          {detailNode.issue_flags.length > 0 && (
            <div className="detail-section">
              <div style={{ fontWeight: 600, fontSize: 11, marginBottom: 6 }}>Issues</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {detailNode.issue_flags.map((flag) => (
                  <span key={flag} className={`issue-badge ${flag}`}>
                    {ISSUE_LABELS[flag] || flag}
                  </span>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => setSelectedNode(null)}
            style={{
              marginTop: 12,
              padding: '4px 10px',
              border: '1px solid var(--border)',
              borderRadius: 4,
              background: 'white',
              fontSize: 11,
              cursor: 'pointer',
            }}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
