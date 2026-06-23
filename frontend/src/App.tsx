import React from 'react';
import { AppStateProvider, useAppState } from './store/appStore';
import Layout from './components/layout/Layout';
import OverviewPage from './components/overview/OverviewPage';
import StructurePage from './components/structure/StructurePage';
import ProvenancePage from './components/provenance/ProvenancePage';
import FailurePage from './components/failure/FailurePage';
import ExperimentPage from './components/experiment/ExperimentPage';

function MainContent() {
  const { sidebarView } = useAppState();

  switch (sidebarView) {
    case 'overview':
      return <OverviewPage />;
    case 'structure':
      return <StructurePage />;
    case 'provenance':
      return <ProvenancePage />;
    case 'failure':
      return <FailurePage />;
    case 'experiment':
      return <ExperimentPage />;
    default:
      return <OverviewPage />;
  }
}

export default function App() {
  return (
    <AppStateProvider>
      <Layout>
        <MainContent />
      </Layout>
    </AppStateProvider>
  );
}
