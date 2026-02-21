'use client';

import { useState } from 'react';
import Link from 'next/link';
import { sendChat } from '@/lib/api';

const USER_ID = 'default-user';
const AGENTS = [
  'STRATEGY_AGENT',
  'MARKETING_AGENT',
  'FINANCE_AGENT',
  'OPS_AGENT',
  'TECH_AGENT',
  'RESEARCH_AGENT',
  'CONTENT_AGENT',
  'LEGAL_AGENT',
  'TASK_AGENT',
] as const;

export default function AgentStudioPage() {
  const [activeAgent, setActiveAgent] = useState<string>(AGENTS[0]);
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = message.trim();
    if (!text || loading) return;
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await sendChat({
        message: text,
        user_id: USER_ID,
        ui_context: 'agent_studio',
        active_agent: activeAgent,
      });
      setResponse(res.response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ minHeight: '100vh', maxWidth: 900, margin: '0 auto', padding: 24 }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24, borderBottom: '1px solid var(--border)', paddingBottom: 16 }}>
        <Link href="/" style={{ color: 'var(--muted)', fontSize: 14 }}>◈ SoloOS</Link>
        <span style={{ color: 'var(--muted)' }}>/</span>
        <strong>Agent Studio</strong>
      </header>

      <p style={{ color: 'var(--muted)', marginBottom: 24 }}>
        Direct access to specialist agents. Skip summaries; get full, detailed output. Disclaimers still apply for Legal and Finance.
      </p>

      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
        {AGENTS.map((name) => (
          <button
            key={name}
            type="button"
            onClick={() => setActiveAgent(name)}
            style={{
              padding: '8px 14px',
              background: activeAgent === name ? 'var(--accent)' : 'var(--surface)',
              color: activeAgent === name ? 'var(--bg)' : 'var(--text)',
              border: `1px solid ${activeAgent === name ? 'var(--accent)' : 'var(--border)'}`,
              borderRadius: 6,
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            {name.replace(/_AGENT$/, '')}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
        <label style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 8 }}>
          Request for {activeAgent}
        </label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={`e.g. ${activeAgent === 'STRATEGY_AGENT' ? 'Analyze my business model for a B2B SaaS' : activeAgent === 'CONTENT_AGENT' ? 'Write a short landing page hero for a productivity app' : 'What do you need?'}`}
          disabled={loading}
          rows={4}
          style={{
            width: '100%',
            padding: 14,
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text)',
            fontSize: 15,
            resize: 'vertical',
          }}
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          style={{
            marginTop: 12,
            padding: '12px 24px',
            background: loading ? 'var(--border)' : 'var(--accent)',
            color: 'var(--bg)',
            border: 'none',
            borderRadius: 8,
            fontWeight: 600,
          }}
        >
          {loading ? 'Running…' : 'Run agent'}
        </button>
      </form>

      {error && (
        <div style={{ padding: 12, background: 'rgba(239,68,68,0.15)', borderRadius: 8, marginBottom: 16, color: '#fca5a5' }}>
          {error}
        </div>
      )}

      {response && (
        <div style={{ padding: 20, background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, whiteSpace: 'pre-wrap' }}>
          {response}
        </div>
      )}
    </main>
  );
}
