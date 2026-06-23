import React from 'react';
import { Play, FlaskConical, Search, Download } from 'lucide-react';
import { useAppState, useAppDispatch } from '../../store/appStore';
import type { RoundName } from '../../types';
import { runDiagnosis, evaluateRetrieval } from '../../utils/api';

const roundOptions: { value: RoundName; label: string }[] = [
  { value: 'round_1', label: 'Round 1' },
  { value: 'round_2', label: 'Round 2' },
  { value: 'round_3', label: 'Round 3' },
  { value: 'repair', label: 'Repair' },
];

export default function TopBar() {
  const { selectedRound } = useAppState();
  const dispatch = useAppDispatch();

  const handleRunDiagnosis = async () => {
    try {
      await runDiagnosis();
    } catch (err) {
      console.error('Diagnosis error:', err);
    }
  };

  const handleRunEvaluation = async () => {
    try {
      await evaluateRetrieval();
    } catch (err) {
      console.error('Evaluation error:', err);
    }
  };

  const handleExport = () => {
    window.open('/api/experiments/export?format=json', '_blank');
  };

  return (
    <div className="topbar">
      <select
        className="topbar-select"
        value={selectedRound}
        onChange={(e) => dispatch({ type: 'SET_SELECTED_ROUND', payload: e.target.value as RoundName })}
      >
        {roundOptions.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>

      <span className="topbar-spacer" />

      <button className="topbar-btn" onClick={handleRunDiagnosis}>
        <FlaskConical size={13} style={{ marginRight: 4 }} />
        Diagnosis
      </button>
      <button className="topbar-btn" onClick={handleRunEvaluation}>
        <Search size={13} style={{ marginRight: 4 }} />
        Evaluate
      </button>
      <button className="topbar-btn" onClick={handleExport}>
        <Download size={13} style={{ marginRight: 4 }} />
        Export
      </button>
    </div>
  );
}
