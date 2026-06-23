import React from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import AgentPanel from './AgentPanel';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-area">
        <TopBar />
        <div className="main-content">
          {children}
        </div>
      </div>
      <AgentPanel />
    </div>
  );
}
