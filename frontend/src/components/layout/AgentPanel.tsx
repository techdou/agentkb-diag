import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAppState } from '../../store/appStore';
import { askAgent } from '../../utils/api';
import type { RoundName } from '../../types';

interface ChatMessage {
  role: 'user' | 'agent';
  text: string;
  sources?: string[];
  timestamp: number;
}

interface KbSummary {
  round: string;
  issueCount: number;
  recall: number;
  orphanCount: number;
  duplicateCount: number;
  conflictCount: number;
}

const suggestedQuestions: Record<RoundName, string[]> = {
  round_1: [
    'What is the KB structure health?',
    'Are there any orphan concepts?',
    'How good is citation coverage?',
  ],
  round_2: [
    'Why is recall@3 dropping?',
    'What new issues appeared in round 2?',
    'Are there duplicate concepts?',
  ],
  round_3: [
    'Why is recall@3 dropping?',
    'What are the top issues?',
    'How can I fix orphan pages?',
    'Which concepts have conflicts?',
  ],
  repair: [
    'Did repair improve recall?',
    'Are all orphans resolved?',
    'What issues remain?',
  ],
};

function getKbSummary(round: RoundName): KbSummary {
  const summaries: Record<RoundName, KbSummary> = {
    round_1: { round: 'Round 1', issueCount: 8, recall: 0.85, orphanCount: 3, duplicateCount: 2, conflictCount: 0 },
    round_2: { round: 'Round 2', issueCount: 18, recall: 0.72, orphanCount: 6, duplicateCount: 5, conflictCount: 3 },
    round_3: { round: 'Round 3', issueCount: 34, recall: 0.55, orphanCount: 11, duplicateCount: 8, conflictCount: 5 },
    repair: { round: 'Repair', issueCount: 12, recall: 0.78, orphanCount: 3, duplicateCount: 2, conflictCount: 1 },
  };
  return summaries[round];
}

export default function AgentPanel() {
  const { selectedRound } = useAppState();
  const [collapsed, setCollapsed] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const kbSummary = getKbSummary(selectedRound);
  const questions = suggestedQuestions[selectedRound] || suggestedQuestions.round_3;

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const addMessage = (msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleSend = async (text?: string) => {
    const question = (text || input).trim();
    if (!question || loading) return;

    setInput('');
    setLoading(true);

    addMessage({ role: 'user', text: question, timestamp: Date.now() });

    try {
      const response = await askAgent(question, selectedRound);
      addMessage({
        role: 'agent',
        text: response.answer,
        sources: response.sources,
        timestamp: Date.now(),
      });
    } catch {
      addMessage({
        role: 'agent',
        text: 'Unable to reach the diagnostic agent. Please ensure the backend is running.',
        timestamp: Date.now(),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (collapsed) {
    return (
      <div
        className="agent-panel collapsed"
        onClick={() => setCollapsed(false)}
        title="Open diagnostic agent"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          paddingTop: 12,
          cursor: 'pointer',
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: 14, lineHeight: 1, userSelect: 'none' }}>&#9664;</span>
        <span
          style={{
            writingMode: 'vertical-rl',
            fontSize: 11,
            color: 'var(--text-secondary)',
            marginTop: 16,
            userSelect: 'none',
            letterSpacing: '0.05em',
            fontWeight: 500,
          }}
        >
          AGENT
        </span>
      </div>
    );
  }

  return (
    <div className="agent-panel">
      {/* Header */}
      <div className="agent-header">
        <span>Diagnostic Agent</span>
        <button className="agent-toggle" onClick={() => setCollapsed(true)} title="Collapse">
          &#9654;
        </button>
      </div>

      {/* Status section */}
      <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--border)', flexShrink: 0, backgroundColor: '#f8fafc' }}>
        <div className="metric-label" style={{ marginBottom: 4 }}>System Status</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 12px', fontSize: 11 }}>
          <span><span style={{ color: 'var(--text-secondary)' }}>Round:</span> <strong>{kbSummary.round}</strong></span>
          <span><span style={{ color: 'var(--text-secondary)' }}>Issues:</span> <strong style={{ color: 'var(--duplicate)' }}>{kbSummary.issueCount}</strong></span>
          <span><span style={{ color: 'var(--text-secondary)' }}>R@3:</span> <strong>{kbSummary.recall.toFixed(2)}</strong></span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 12px', marginTop: 4, fontSize: 10.5 }}>
          <span style={{ color: 'var(--orphan)' }}>&#9679; Orphans: {kbSummary.orphanCount}</span>
          <span style={{ color: 'var(--duplicate)' }}>&#9679; Duplicates: {kbSummary.duplicateCount}</span>
          <span style={{ color: 'var(--conflict)' }}>&#9679; Conflicts: {kbSummary.conflictCount}</span>
        </div>
      </div>

      {/* Suggested questions */}
      <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
        <div className="metric-label" style={{ marginBottom: 4 }}>Suggested Questions</div>
        {questions.map((q, i) => (
          <button
            key={i}
            className="suggested-q"
            onClick={() => handleSend(q)}
            disabled={loading}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px 12px' }}>
        {messages.length === 0 && (
          <div style={{ color: 'var(--text-secondary)', fontSize: 11.5, textAlign: 'center', padding: '20px 8px', lineHeight: 1.5 }}>
            Ask the diagnostic agent about KB health, retrieval degradation, or specific issues.
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg ${msg.role}`}>
            <span className="chat-bubble">{msg.text}</span>
            {msg.sources && msg.sources.length > 0 && (
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
                Sources: {msg.sources.join(', ')}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-msg agent">
            <span className="chat-bubble">Analyzing...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-row" style={{ padding: '8px 12px', borderTop: '1px solid var(--border)', flexShrink: 0 }}>
        <input
          className="chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything..."
          disabled={loading}
        />
        <button
          className="chat-send"
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
