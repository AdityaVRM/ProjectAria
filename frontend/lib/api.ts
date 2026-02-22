const API = process.env.NEXT_PUBLIC_API_URL || '/api';

export type UIContext = 'chat' | 'dashboard' | 'agent_studio';

export interface ChatRequest {
  message: string;
  user_id: string;
  session_id?: string;
  ui_context?: UIContext;
  active_agent?: string;
}

export interface ChatResponse {
  response: string;
  user_id: string;
}

export interface BusinessSnapshot {
  user_id: string;
  business_name: string;
  one_liner: string;
  stage: string;
  industry: string;
  target_customer: string;
  current_mrr: string;
  primary_goal_90_days: string;
  completed_milestones: string[];
  active_projects: string[];
  pending_tasks: string[];
  key_decisions: string[];
  blockers: string[];
  last_updated: string;
  capacity_hours_per_week: string;
}

export interface AgentResult {
  agent_name: string;
  status: 'completed' | 'error' | 'running' | 'iterating';
  output: Record<string, unknown>;
  summary: string;
  iteration: number;
}

export interface RunRequest {
  message: string;
  user_id: string;
}

export interface RunResponse {
  intent: string;
  is_new_user: boolean;
  synthesis: string;
  agent_results: AgentResult[];
  onboarding: boolean;
  agent_plan: string[][];
}

export interface IterateRequest {
  user_id: string;
  agent_name: string;
  feedback: string;
  original_message?: string;
  previous_output?: Record<string, unknown>;
  iteration?: number;
}

export interface IterateResponse {
  agent_name: string;
  status: 'completed' | 'error';
  output: Record<string, unknown>;
  summary: string;
  iteration: number;
}

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: req.message,
      user_id: req.user_id,
      session_id: req.session_id ?? null,
      ui_context: req.ui_context ?? 'chat',
      active_agent: req.active_agent ?? null,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Chat failed');
  }
  return res.json();
}

export async function runOrchestration(req: RunRequest): Promise<RunResponse> {
  const res = await fetch(`${API}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Run failed');
  }
  return res.json();
}

export async function iterateAgent(req: IterateRequest): Promise<IterateResponse> {
  const res = await fetch(`${API}/agent/iterate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Iterate failed');
  }
  return res.json();
}

export async function getMemory(userId: string): Promise<BusinessSnapshot> {
  const res = await fetch(`${API}/memory/${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error('Failed to load memory');
  return res.json();
}

export async function mergeMemory(userId: string, updates: Partial<BusinessSnapshot>): Promise<BusinessSnapshot> {
  const res = await fetch(`${API}/memory/${encodeURIComponent(userId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error('Failed to update memory');
  return res.json();
}
