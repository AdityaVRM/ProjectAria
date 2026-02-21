'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { sendChat } from '@/lib/api';

const USER_ID = 'default-user';

export default function ChatPage() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = message.trim();
    if (!text || loading) return;
    setMessage('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setLoading(true);
    setError(null);
    try {
      const res = await sendChat({
        message: text,
        user_id: USER_ID,
        ui_context: 'chat',
      });
      setMessages((prev) => [...prev, { role: 'assistant', content: res.response }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', maxWidth: 720, margin: '0 auto', padding: 24 }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24, borderBottom: '1px solid var(--border)', paddingBottom: 16 }}>
        <Link href="/" style={{ color: 'var(--muted)', fontSize: 14 }}>◈ SoloOS</Link>
        <span style={{ color: 'var(--muted)' }}>/</span>
        <strong>Chat with ARIA</strong>
      </header>

      <div style={{ flex: 1, overflow: 'auto', marginBottom: 24 }}>
        {messages.length === 0 && (
          <p style={{ color: 'var(--muted)', fontStyle: 'italic' }}>
            Say what you&apos;re working on — a business idea, a problem, or a goal. ARIA will orchestrate the right agents and give you a clear action plan.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              marginBottom: 16,
              padding: 16,
              background: m.role === 'user' ? 'var(--surface)' : 'transparent',
              border: m.role === 'user' ? '1px solid var(--border)' : 'none',
              borderRadius: 8,
              whiteSpace: 'pre-wrap',
            }}
          >
            <span style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4, display: 'block' }}>
              {m.role === 'user' ? 'You' : 'ARIA'}
            </span>
            {m.content}
          </div>
        ))}
        {loading && (
          <div style={{ color: 'var(--muted)', fontStyle: 'italic' }}>ARIA is thinking…</div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <div style={{ padding: 12, background: 'rgba(239,68,68,0.15)', borderRadius: 8, marginBottom: 16, color: '#fca5a5' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Describe your idea, problem, or goal…"
          disabled={loading}
          style={{
            flex: 1,
            padding: 14,
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text)',
            fontSize: 16,
          }}
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          style={{
            padding: '14px 24px',
            background: loading ? 'var(--border)' : 'var(--accent)',
            color: 'var(--bg)',
            border: 'none',
            borderRadius: 8,
            fontWeight: 600,
          }}
        >
          Send
        </button>
      </form>
    </main>
  );
}
