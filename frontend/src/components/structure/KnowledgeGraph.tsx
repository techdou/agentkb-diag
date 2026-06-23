import React from 'react';
import { useAppDispatch } from '../../store/appStore';
import type { LinkGraph, GraphNode, GraphEdge } from '../../types';

interface KnowledgeGraphProps {
  graph: LinkGraph;
  filter?: string;
}

const NODE_RADIUS = 18;
const CENTER_X = 500;
const CENTER_Y = 350;
const LAYOUT_RADIUS = 280;

function getNodeColor(node: GraphNode): string {
  if (node.issue_flags.includes('orphan')) return '#ef4444';
  if (node.issue_flags.includes('duplicate')) return '#f97316';
  if (node.issue_flags.includes('conflict')) return '#a855f7';
  if (node.issue_flags.includes('broken_link')) return '#eab308';
  if (node.issue_flags.includes('missing_citation')) return '#06b6d4';
  return '#94a3b8';
}

function getNodeStroke(node: GraphNode): string {
  if (node.issue_flags.length > 0) return getNodeColor(node);
  return '#94a3b8';
}

function getNodeStrokeWidth(node: GraphNode): number {
  return node.issue_flags.length > 0 ? 3 : 1;
}

export default function KnowledgeGraph({ graph, filter }: KnowledgeGraphProps) {
  const dispatch = useAppDispatch();

  const filteredNodes = React.useMemo(() => {
    if (!filter || filter === 'all') return graph.nodes;
    return graph.nodes.filter((n) => n.issue_flags.includes(filter));
  }, [graph.nodes, filter]);

  const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));
  const filteredEdges = graph.edges.filter(
    (e) => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target)
  );

  const positions = React.useMemo(() => {
    const map: Record<string, { x: number; y: number }> = {};
    filteredNodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / filteredNodes.length - Math.PI / 2;
      map[node.id] = {
        x: CENTER_X + LAYOUT_RADIUS * Math.cos(angle),
        y: CENTER_Y + LAYOUT_RADIUS * Math.sin(angle),
      };
    });
    return map;
  }, [filteredNodes]);

  const handleNodeClick = (nodeId: string) => {
    dispatch({ type: 'SET_SELECTED_PAGE_ID', payload: nodeId });
  };

  if (filteredNodes.length === 0) {
    return (
      <div className="graph-container flex items-center justify-center" style={{ color: 'var(--color-text-secondary)' }}>
        No nodes match the current filter.
      </div>
    );
  }

  return (
    <div className="graph-container">
      <svg
        className="graph-svg"
        viewBox="0 0 1000 700"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Edges */}
        {filteredEdges.map((edge, i) => {
          const source = positions[edge.source];
          const target = positions[edge.target];
          if (!source || !target) return null;
          return (
            <line
              key={`edge-${i}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              className="graph-edge"
              opacity={edge.confidence}
            />
          );
        })}

        {/* Nodes */}
        {filteredNodes.map((node) => {
          const pos = positions[node.id];
          if (!pos) return null;
          const color = getNodeStroke(node);
          const strokeWidth = getNodeStrokeWidth(node);
          const nodeText = node.label.length > 18 ? node.label.substring(0, 16) + '..' : node.label;
          const textOffset = NODE_RADIUS + 14;

          return (
            <g key={node.id} className="graph-node" onClick={() => handleNodeClick(node.id)}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r={NODE_RADIUS}
                fill={node.issue_flags.length > 0 ? '#ffffff' : '#cbd5e1'}
                stroke={color}
                strokeWidth={strokeWidth}
              />
              {node.issue_flags.length > 0 && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={6}
                  fill={color}
                />
              )}
              <text
                x={pos.x}
                y={pos.y + textOffset}
                className="graph-node-label"
              >
                {nodeText}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
