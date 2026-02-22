'use client';

import { useState, useCallback, FormEvent } from 'react';
import { runOrchestration, iterateAgent, AgentResult, sendChat } from '@/lib/api';

const USER_ID = 'solo-user-1';

const AGENT_META: Record<string, { label: string; icon: string }> = {
  STRATEGY_AGENT: { label: 'Strategy', icon: '\u265F' },
  MARKETING_AGENT: { label: 'Marketing', icon: '\u2692' },
  FINANCE_AGENT: { label: 'Finance', icon: '\u2696' },
  OPS_AGENT: { label: 'Operations', icon: '\u2699' },
  TECH_AGENT: { label: 'Tech', icon: '\u2318' },
  RESEARCH_AGENT: { label: 'Research', icon: '\u2315' },
  CONTENT_AGENT: { label: 'Content', icon: '\u270E' },
  LEGAL_AGENT: { label: 'Legal', icon: '\u2694' },
  TASK_AGENT: { label: 'Tasks', icon: '\u2611' },
};

const STATUS_COLORS: Record<string, string> = {
  completed: 'var(--success)',
  error: 'var(--error)',
  running: 'var(--warning)',
  iterating: 'var(--accent)',
};

function AgentOutputDisplay({ output }: { output: Record<string, unknown> }) {
  return (
    <div style={{ fontSize: 14, lineHeight: 1.7 }}>
      {Object.entries(output).map(([key, value]) => {
        if (key === 'disclaimer' && typeof value === 'string') {
          return (
            <p key={key} style={{ color: 'var(--warning)', fontStyle: 'italic', fontSize: 12, marginTop: 12 }}>
              {value}
            </p>
          );
        }
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        if (typeof value === 'string') {
          return (
            <div key={key} style={{ marginBottom: 12 }}>
              <strong style={{ color: 'var(--accent)', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</strong>
              <p style={{ margin: '4px 0 0', whiteSpace: 'pre-wrap' }}>{value}</p>
            </div>
          );
        }
        if (Array.isArray(value)) {
          return (
            <div key={key} style={{ marginBottom: 12 }}>
              <strong style={{ color: 'var(--accent)', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</strong>
              <ul style={{ margin: '4px 0 0', paddingLeft: 20 }}>
                {value.map((item, i) => (
                  <li key={i} style={{ marginBottom: 4 }}>
                    {typeof item === 'object' ? JSON.stringify(item, null, 2) : String(item)}
                  </li>
                ))}
              </ul>
            </div>
          );
        }
        if (typeof value === 'object' && value !== null) {
          return (
            <div key={key} style={{ marginBottom: 12 }}>
              <strong style={{ color: 'var(--accent)', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</strong>
              <pre style={{ margin: '4px 0 0', fontSize: 13, background: 'var(--bg)', padding: 10, borderRadius: 6, overflow: 'auto', maxHeight: 200 }}>
                {JSON.stringify(value, null, 2)}
              </pre>
            </div>
          );
        }
        return null;
      })}
    </div>
  );
}

export default function WorkspacePage() {
  const [input, setInput] = useState('');
  const [lastMessage, setLastMessage] = useState('');
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const [synthesis, setSynthesis] = useState('');
  const [agentResults, setAgentResults] = useState<AgentResult[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [iteratingAgents, setIteratingAgents] = useState<Record<string, boolean>>({});
  const [feedbackInputs, setFeedbackInputs] = useState<Record<string, string>>({});
  const [showFeedbackForm, setShowFeedbackForm] = useState<Record<string, boolean>>({});
  const [isOnboarding, setIsOnboarding] = useState(false);
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [chatInput, setChatInput] = useState('');

  const handleRun = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    const msg = input.trim();
    if (!msg || running) return;
    setRunning(true);
    setError('');
    setSynthesis('');
    setAgentResults([]);
    setExpanded({});
    setLastMessage(msg);
    setInput('');
    setIsOnboarding(false);
    setChatMessages([]);

    try {
      const res = await runOrchestration({ message: msg, user_id: USER_ID });
      setSynthesis(res.synthesis);
      setAgentResults(res.agent_results || []);
      if (res.onboarding) {
        setIsOnboarding(true);
        setChatMessages([
          { role: 'user', content: msg },
          { role: 'assistant', content: res.synthesis },
        ]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setRunning(false);
    }
  }, [input, running]);

  const handleIterate = useCallback(async (agentName: string) => {
    const feedback = feedbackInputs[agentName]?.trim();
    if (!feedback) return;
    const existing = agentResults.find(a => a.agent_name === agentName);
    setIteratingAgents(prev => ({ ...prev, [agentName]: true }));
    setAgentResults(prev => prev.map(a =>
      a.agent_name === agentName ? { ...a, status: 'iterating' as const } : a
    ));

    try {
      const res = await iterateAgent({
        user_id: USER_ID,
        agent_name: agentName,
        feedback,
        original_message: lastMessage,
        previous_output: existing?.output || {},
        iteration: existing?.iteration || 1,
      });
      setAgentResults(prev => prev.map(a =>
        a.agent_name === agentName ? { ...res, status: res.status as AgentResult['status'] } : a
      ));
      setFeedbackInputs(prev => ({ ...prev, [agentName]: '' }));
      setShowFeedbackForm(prev => ({ ...prev, [agentName]: false }));
    } catch (err) {
      setAgentResults(prev => prev.map(a =>
        a.agent_name === agentName ? { ...a, status: 'error' as const } : a
      ));
      setError(err instanceof Error ? err.message : 'Iteration failed');
    } finally {
      setIteratingAgents(prev => ({ ...prev, [agentName]: false }));
    }
  }, [feedbackInputs, agentResults, lastMessage]);

  const handleChatSend = useCallback(async () => {
    const msg = chatInput.trim();
    if (!msg) return;
    setChatMessages(prev => [...prev, { role: 'user', content: msg }]);
    setChatInput('');
    setRunning(true);
    try {
      const res = await sendChat({ message: msg, user_id: USER_ID, ui_context: 'chat' });
      setChatMessages(prev => [...prev, { role: 'assistant', content: res.response }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err instanceof Error ? err.message : 'failed'}` }]);
    } finally {
      setRunning(false);
    }
  }, [chatInput]);

  const hasResults = synthesis || agentResults.length > 0;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      {/* Header */}
      <header style={{
        position: 'sticky', top: 0, zIndex: 50, backdropFilter: 'blur(12px)',
        background: 'rgba(13,13,15,0.85)', borderBottom: '1px solid var(--border)',
        padding: '12px 24px', display: 'flex', alignItems: 'center', gap: 16,
      }}>
        <span style={{ fontSize: 20, fontWeight: 700 }}>SoloOS</span>
        <span style={{ color: 'var(--muted)', fontSize: 13 }}>Workspace</span>
        <div style={{ flex: 1 }} />
        <span style={{ color: 'var(--muted)', fontSize: 12 }}>
          {agentResults.length > 0 ? `${agentResults.length} agents ran` : 'Ready'}
        </span>
      </header>

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '32px 20px' }}>
        {/* Empty state / Input */}
        {!hasResults && !running && (
          <div style={{ textAlign: 'center', paddingTop: 80, paddingBottom: 40 }}>
            <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>What are you building?</h1>
            <p style={{ color: 'var(--muted)', fontSize: 16, maxWidth: 500, margin: '0 auto 40px' }}>
              Describe your idea, problem, or goal. ARIA will dispatch your AI team and bring back actionable results.
            </p>
          </div>
        )}

        <form onSubmit={handleRun} style={{ marginBottom: 32 }}>
          <div style={{
            display: 'flex', gap: 10, background: 'var(--surface)',
            border: '1px solid var(--border)', borderRadius: 12, padding: 6,
          }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder={hasResults ? 'Ask a follow-up or describe a new goal...' : 'e.g. I want to build a SaaS for freelancers to manage invoices...'}
              disabled={running}
              style={{
                flex: 1, background: 'transparent', border: 'none', outline: 'none',
                color: 'var(--text)', padding: '12px 14px', fontSize: 15,
              }}
            />
            <button
              type="submit"
              disabled={running || !input.trim()}
              style={{
                background: running ? 'var(--border)' : 'var(--accent)',
                color: running ? 'var(--muted)' : '#000',
                border: 'none', borderRadius: 8, padding: '10px 24px',
                fontWeight: 600, fontSize: 14, whiteSpace: 'nowrap',
              }}
            >
              {running ? 'Running...' : 'Run'}
            </button>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div style={{
            background: 'rgba(248,113,113,0.1)', border: '1px solid var(--error)',
            borderRadius: 8, padding: '12px 16px', marginBottom: 24, color: 'var(--error)',
          }}>
            {error}
          </div>
        )}

        {/* Loading */}
        {running && (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <div style={{
              width: 40, height: 40, border: '3px solid var(--border)',
              borderTopColor: 'var(--accent)', borderRadius: '50%',
              animation: 'spin 0.8s linear infinite', margin: '0 auto 16px',
            }} />
            <p style={{ color: 'var(--muted)' }}>ARIA is orchestrating your AI team...</p>
          </div>
        )}

        {/* Onboarding chat */}
        {isOnboarding && !running && (
          <div style={{
            background: 'var(--surface)', borderRadius: 12,
            border: '1px solid var(--border)', padding: 24, marginBottom: 32,
          }}>
            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Onboarding with ARIA</h3>
            <div style={{ maxHeight: 400, overflowY: 'auto', marginBottom: 16 }}>
              {chatMessages.map((m, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
                  marginBottom: 10,
                }}>
                  <div style={{
                    maxWidth: '80%', padding: '10px 14px', borderRadius: 10,
                    background: m.role === 'user' ? 'var(--accent-dim)' : 'var(--bg)',
                    fontSize: 14, whiteSpace: 'pre-wrap', lineHeight: 1.6,
                  }}>
                    {m.content}
                  </div>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleChatSend()}
                placeholder="Reply to ARIA..."
                style={{
                  flex: 1, background: 'var(--bg)', border: '1px solid var(--border)',
                  borderRadius: 8, padding: '10px 14px', color: 'var(--text)', fontSize: 14, outline: 'none',
                }}
              />
              <button onClick={handleChatSend} disabled={running} style={{
                background: 'var(--accent)', color: '#000', border: 'none',
                borderRadius: 8, padding: '10px 18px', fontWeight: 600,
              }}>
                Send
              </button>
            </div>
          </div>
        )}

        {/* ARIA Synthesis */}
        {synthesis && !isOnboarding && !running && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(167,139,250,0.08), rgba(124,58,237,0.04))',
            border: '1px solid rgba(167,139,250,0.2)', borderRadius: 12,
            padding: 24, marginBottom: 32,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <span style={{ fontSize: 18 }}>ARIA</span>
              <span style={{ color: 'var(--muted)', fontSize: 12 }}>Executive Summary</span>
            </div>
            <div style={{ fontSize: 15, lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>
              {synthesis}
            </div>
          </div>
        )}

        {/* Agent Result Cards */}
        {agentResults.length > 0 && !running && (
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: 16, marginBottom: 32,
          }}>
            {agentResults.map((agent) => {
              const meta = AGENT_META[agent.agent_name] || { label: agent.agent_name, icon: '\u25C6' };
              const isExp = expanded[agent.agent_name];
              const isIterating = iteratingAgents[agent.agent_name];
              const showFb = showFeedbackForm[agent.agent_name];

              return (
                <div key={agent.agent_name} style={{
                  background: 'var(--surface)', border: '1px solid var(--border)',
                  borderRadius: 12, overflow: 'hidden', transition: 'border-color 0.2s',
                }}>
                  {/* Card Header */}
                  <div
                    onClick={() => setExpanded(prev => ({ ...prev, [agent.agent_name]: !isExp }))}
                    style={{
                      padding: '14px 18px', cursor: 'pointer', display: 'flex',
                      alignItems: 'center', gap: 10, borderBottom: isExp ? '1px solid var(--border)' : 'none',
                    }}
                  >
                    <span style={{ fontSize: 18 }}>{meta.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{meta.label}</div>
                      {agent.summary && (
                        <div style={{ color: 'var(--muted)', fontSize: 12, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 220 }}>
                          {agent.summary.slice(0, 80)}...
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {agent.iteration > 1 && (
                        <span style={{ fontSize: 11, color: 'var(--accent)', background: 'rgba(167,139,250,0.15)', padding: '2px 8px', borderRadius: 10 }}>
                          v{agent.iteration}
                        </span>
                      )}
                      <span style={{
                        width: 8, height: 8, borderRadius: '50%',
                        background: STATUS_COLORS[agent.status] || 'var(--muted)',
                      }} />
                      <span style={{ fontSize: 16, color: 'var(--muted)' }}>{isExp ? '\u25B2' : '\u25BC'}</span>
                    </div>
                  </div>

                  {/* Card Body */}
                  {isExp && (
                    <div style={{ padding: '16px 18px' }}>
                      {agent.status === 'error' ? (
                        <p style={{ color: 'var(--error)' }}>{JSON.stringify(agent.output)}</p>
                      ) : (
                        <AgentOutputDisplay output={agent.output} />
                      )}

                      {/* Iterate controls */}
                      <div style={{ marginTop: 16, borderTop: '1px solid var(--border)', paddingTop: 12 }}>
                        {!showFb ? (
                          <button
                            onClick={() => setShowFeedbackForm(prev => ({ ...prev, [agent.agent_name]: true }))}
                            style={{
                              background: 'transparent', border: '1px solid var(--border)',
                              color: 'var(--accent)', borderRadius: 6, padding: '6px 14px',
                              fontSize: 12, fontWeight: 600,
                            }}
                          >
                            Iterate with feedback
                          </button>
                        ) : (
                          <div>
                            <textarea
                              value={feedbackInputs[agent.agent_name] || ''}
                              onChange={e => setFeedbackInputs(prev => ({ ...prev, [agent.agent_name]: e.target.value }))}
                              placeholder="Tell this agent what to improve..."
                              rows={3}
                              style={{
                                width: '100%', background: 'var(--bg)', border: '1px solid var(--border)',
                                borderRadius: 8, padding: 10, color: 'var(--text)', fontSize: 13,
                                resize: 'vertical', outline: 'none',
                              }}
                            />
                            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                              <button
                                onClick={() => handleIterate(agent.agent_name)}
                                disabled={isIterating || !feedbackInputs[agent.agent_name]?.trim()}
                                style={{
                                  background: isIterating ? 'var(--border)' : 'var(--accent)',
                                  color: isIterating ? 'var(--muted)' : '#000',
                                  border: 'none', borderRadius: 6, padding: '6px 16px',
                                  fontSize: 12, fontWeight: 600,
                                }}
                              >
                                {isIterating ? 'Re-running...' : 'Re-run agent'}
                              </button>
                              <button
                                onClick={() => setShowFeedbackForm(prev => ({ ...prev, [agent.agent_name]: false }))}
                                style={{
                                  background: 'transparent', border: '1px solid var(--border)',
                                  color: 'var(--muted)', borderRadius: 6, padding: '6px 12px', fontSize: 12,
                                }}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
