import Link from 'next/link';

export default function Home() {
  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: 8 }}>
        ◈ SoloOS
      </h1>
      <p style={{ color: 'var(--muted)', marginBottom: 32 }}>
        Multi-Agent Orchestration Platform for Solopreneurs
      </p>
      <nav style={{ display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
        <Link href="/chat" style={{ padding: '12px 24px', background: 'var(--accent)', color: 'var(--bg)', borderRadius: 8, fontWeight: 600 }}>
          Chat with ARIA
        </Link>
        <Link href="/dashboard" style={{ padding: '12px 24px', background: 'var(--surface)', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: 8, fontWeight: 600 }}>
          Dashboard
        </Link>
        <Link href="/agent-studio" style={{ padding: '12px 24px', background: 'var(--surface)', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: 8, fontWeight: 600 }}>
          Agent Studio
        </Link>
      </nav>
    </main>
  );
}
