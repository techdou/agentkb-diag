import React from 'react';

interface IssueFilterProps {
  value: string;
  onChange: (value: string) => void;
}

const filters = [
  { value: 'all', label: 'All' },
  { value: 'orphan', label: 'Orphan' },
  { value: 'duplicate', label: 'Duplicate' },
  { value: 'conflict', label: 'Conflict' },
  { value: 'broken_link', label: 'Broken Link' },
];

export default function IssueFilter({ value, onChange }: IssueFilterProps) {
  return (
    <div className="issue-filter">
      {filters.map((f) => (
        <button
          key={f.value}
          className={`filter-btn${value === f.value ? ' active' : ''}`}
          onClick={() => onChange(f.value)}
        >
          {f.label}
        </button>
      ))}
    </div>
  );
}
