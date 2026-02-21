# ◈ SoloOS — Agentic OS

Multi-Agent Orchestration Platform for Solopreneurs. ARIA (Adaptive Resource & Intelligence Agent) orchestrates 10 specialist agents to help you build, grow, and run your business.

## Stack

- **Orchestration**: LangGraph (Python)
- **LLM**: Claude (Anthropic API)
- **Backend**: FastAPI
- **Frontend**: Next.js 14 + TypeScript
- **Memory**: In-memory / SQLite (upgrade to Pinecone + PostgreSQL for production)

## Quick Start

```bash
# Backend (use venv for deps)
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # then set CURSOR_COMPOSER_1_5_API_KEY in .env
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Set `CURSOR_COMPOSER_1_5_API_KEY` in `backend/.env` (or `ANTHROPIC_API_KEY` as fallback). The frontend proxies `/api/*` to the backend (see `next.config.js`).

## Agents

| Agent | Role |
|-------|------|
| ARIA | Orchestrator — understands intent, dispatches agents, synthesizes output |
| STRATEGY_AGENT | Business model, positioning, market sizing |
| MARKETING_AGENT | Content strategy, campaigns, SEO, copy |
| FINANCE_AGENT | Pricing, P&L, unit economics, funding paths |
| OPS_AGENT | SOPs, workflows, tool stack, automation |
| TECH_AGENT | MVP scope, tech stack, architecture |
| RESEARCH_AGENT | Market research, competitor intel, validation |
| CONTENT_AGENT | Blog, email, social, landing page copy |
| TASK_AGENT | Master to-do lists, sprints, milestones |
| LEGAL_AGENT | Entity structure, contracts, IP (disclaimer) |
| MEMORY_AGENT | Persistent business context across sessions |

## Implementation map (spec → code)

| Spec section | Location |
|-------------|----------|
| §1 Master system prompt (ARIA) | `backend/app/prompts/aria.py` |
| §2 Specialist prompts | `backend/app/prompts/specialists.py` |
| §3 Orchestration logic | `backend/app/orchestration/nodes.py` + `graph.py` |
| §4 Onboarding | `backend/app/prompts/onboarding.py`; used in `nodes.py` (onboarding_response) |
| §5 Frontend context | `backend/app/prompts/context.py`; injected in classifier + synthesize |
| §6 Integration (web search, docs) | RESEARCH_AGENT uses LLM only; add a web-search tool in `agents/invoke.py` for §6.1 |
| §7 Safety / guardrails | `backend/app/prompts/safety.py`; appended to all agents in `agents/invoke.py` |
| §8 Tech stack | This repo (LangGraph, FastAPI, Next.js 14) |

## License

Confidential — February 2026.
# ProjectAria
# ProjectAria
