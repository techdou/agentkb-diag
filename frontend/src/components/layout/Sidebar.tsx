import React from 'react';
import { BarChart3, Network, GitBranch, XCircle, FlaskConical } from 'lucide-react';
import { useAppState, useAppDispatch } from '../../store/appStore';
import type { SidebarView } from '../../types';

const navItems: { view: SidebarView; label: string; icon: React.ReactNode }[] = [
  { view: 'overview', label: 'Overview', icon: <BarChart3 size={16} /> },
  { view: 'structure', label: 'Structure', icon: <Network size={16} /> },
  { view: 'provenance', label: 'Provenance', icon: <GitBranch size={16} /> },
  { view: 'failure', label: 'Failure', icon: <XCircle size={16} /> },
  { view: 'experiment', label: 'Experiment', icon: <FlaskConical size={16} /> },
];

export default function Sidebar() {
  const { sidebarView } = useAppState();
  const dispatch = useAppDispatch();

  return (
    <div className="sidebar">
      <div className="sidebar-title">AgentKB-Diag</div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.view}
            className={`sidebar-item${sidebarView === item.view ? ' active' : ''}`}
            onClick={() => dispatch({ type: 'SET_SIDEBAR_VIEW', payload: item.view })}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
