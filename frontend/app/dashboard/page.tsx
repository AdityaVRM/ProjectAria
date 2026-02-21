'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getMemory, sendChat } from '@/lib/api';
import type { BusinessSnapshot } from '@/lib/api';

const USER_ID = 'default-user';

export default function DashboardPage() {
  const [snapshot, setSnapshot] = useState<BusinessSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [prompt, setPrompt] = useState('');
  const [taskOutput, setTaskOutput] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    getMemory(USER_ID)
      .then(setSnapshot)
      .catch(() => setSnapshot(null))
      .finally(() => setLoading(false));
  }, []);

  async function askForTasks() {
    if (!prompt.trim() || sending) return;
    setSending(true);
    setTaskOutput(null);
    try {
      const res = await sendChat({
        message: prompt.trim(),
        user_id: USER_ID,
        ui_context: 'dashboard',
      });
      setTaskOutput(res.response);
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return (
      <main style={{ minHeight: '100vh', padding: 24 }}>
        <p style={{ color: 'var(--muted)' }}>Loading dashboard…</p>
      </main>
    );
  }

  return (
    <main style={{ minHeight: '100vh', maxWidth: 900, margin: '0 auto', padding: 24 }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 32, borderBottom: '1px solid var(--border)', paddingBottom: 16 }}>
        <Link href="/" style={{ color: 'var(--muted)', fontSize: 14 }}>◈ SoloOS</Link>
        <span style={{ color: 'var(--muted)' }}>/</span>
        <strong>Dashboard</strong>
      </header>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Business snapshot</h2>
        <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, padding: 20 }}>
          {snapshot?.business_name ? (
            <ul style={{ margin: 0, paddingLeft: 20, color: 'var(--text)' }}>
              <li><strong>Name:</strong> {snapshot.business_name}</li>
              <li><strong>One-liner:</strong> {snapshot.one_liner || '—'}</li>
              <li><strong>Stage:</strong> {snapshot.stage || '—'}</li>
              <li><strong>Industry:</strong> {snapshot.industry || '—'}</li>
              <li><strong>Target customer:</strong> {snapshot.target_customer || '—'}</li>
              <li><strong>90-day goal:</strong> {snapshot.primary_goal_90_days || '—'}</li>
              <li><strong>Capacity:</strong> {snapshot.capacity_hours_per_week || '—'} hrs/week</li>
              {(snapshot.pending_tasks?.length ?? 0) > 0 && (
                <li><strong>Pending tasks:</strong> <ul style={{ marginTop: 4 }}>{snapshot.pending_tasks?.map((t, i) => <li key={i}>{t}</li>)}</ul></li>
              )}
            </ul>
          ) : (
            <p style={{ color: 'var(--muted)', margin: 0 }}>No business context yet. Start in Chat to onboard.</p>
          )}
        </div>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Update tasks (Dashboard context)</h2>
        <p style={{ color: 'var(--muted)', fontSize: 14, marginBottom: 12 }}>
          Ask ARIA to update your plan; responses are structured for this view and will update the task board.
        </p>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Give me this week's priority tasks"
            disabled={sending}
            style={{
              flex: 1,
              padding: 12,
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              color: 'var(--text)',
            }}
          />
          <button
            type="button"
            onClick={askForTasks}
            disabled={sending || !prompt.trim()}
            style={{
              padding: '12px 20px',
              background: 'var(--accent)',
              color: 'var(--bg)',
              border: 'none',
              borderRadius: 8,
              fontWeight: 600,
            }}
          >
            {sending ? '…' : 'Ask'}
          </button>
        </div>
        {taskOutput && (
          <div style={{ marginTop: 16, padding: 16, background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, whiteSpace: 'pre-wrap' }}>
            {taskOutput}
          </div>
        )}
      </section>
    </main>
  );
}
