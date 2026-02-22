"""SoloOS Backend — FastAPI app and routes."""
import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import ChatRequest, RunRequest, IterateRequest, BusinessSnapshot
from app.orchestration import run_orchestrator, run_orchestrator_structured
from app.orchestration.nodes import AGENT_INVOKERS
from app.memory import get_memory_store, memory_agent_get_snapshot, memory_agent_update


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="SoloOS — Agentic OS",
    description="Multi-Agent Orchestration Platform for Solopreneurs",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _handle_llm_error(e: Exception):
    err = str(e)
    if "API key" in err or "GEMINI" in err:
        raise HTTPException(503, "Gemini API key not configured. Set GEMINI_API_KEY in backend/.env")
    if "API_KEY_INVALID" in err or "API key not valid" in err:
        raise HTTPException(503, "Gemini API key is invalid. Check GEMINI_API_KEY in backend/.env")
    raise HTTPException(500, err)


def _agent_summary(output: Any) -> str:
    if not isinstance(output, dict):
        return ""
    for v in output.values():
        if isinstance(v, str) and len(v) > 20:
            return v[:300]
    return ""


@app.get("/health")
def health():
    return {"status": "ok", "service": "solos-api"}


@app.post("/run")
def run(req: RunRequest) -> dict:
    message = req.message.strip()
    if not message:
        raise HTTPException(400, "message is required")
    try:
        result = run_orchestrator_structured(user_id=req.user_id, user_message=message)
    except (ValueError, Exception) as e:
        _handle_llm_error(e)

    agent_outputs = result.get("agent_outputs") or {}
    agent_results = []
    for name, output in agent_outputs.items():
        agent_results.append({
            "agent_name": name,
            "status": "error" if isinstance(output, dict) and "error" in output else "completed",
            "output": output if isinstance(output, dict) else {"raw": str(output)},
            "summary": _agent_summary(output),
            "iteration": 1,
        })

    return {
        "intent": result.get("intent", ""),
        "is_new_user": result.get("is_new_user", False),
        "synthesis": result.get("final_response", ""),
        "agent_results": agent_results,
        "onboarding": result.get("intent") == "ONBOARDING",
        "agent_plan": result.get("agent_plan", []),
    }


@app.post("/agent/iterate")
def iterate_agent(req: IterateRequest) -> dict:
    invoker = AGENT_INVOKERS.get(req.agent_name)
    if not invoker:
        raise HTTPException(400, f"Unknown agent: {req.agent_name}")

    snapshot = memory_agent_get_snapshot(req.user_id)
    bc = json.dumps({
        "business_name": snapshot.business_name,
        "one_liner": snapshot.one_liner,
        "stage": snapshot.stage,
        "industry": snapshot.industry,
        "target_customer": snapshot.target_customer,
        "primary_goal_90_days": snapshot.primary_goal_90_days,
    })
    inputs: dict[str, Any] = {
        "business_context": bc,
        "specific_question": req.original_message,
        "constraints": (
            f"USER FEEDBACK on your previous output:\n{req.feedback}\n\n"
            f"Your previous output:\n{json.dumps(req.previous_output, indent=2)[:4000]}\n\n"
            "Improve your response based on this feedback. Be more thorough and specific."
        ),
    }
    try:
        output = invoker(inputs)
    except Exception as e:
        _handle_llm_error(e)

    summary = _agent_summary(output)
    key = req.agent_name.replace("_AGENT", "").lower()
    memory_agent_update(req.user_id, {"agent_outputs_summary": {key: summary[:200]}})

    return {
        "agent_name": req.agent_name,
        "status": "error" if isinstance(output, dict) and "error" in output else "completed",
        "output": output,
        "summary": summary,
        "iteration": req.iteration + 1,
    }


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    message = req.message.strip()
    if not message:
        raise HTTPException(400, "message is required")
    if req.active_agent and message.startswith(f"[Agent Studio - {req.active_agent}]"):
        message = message.split("\n", 1)[-1].strip() or message
    try:
        response_text = run_orchestrator(
            user_id=req.user_id, user_message=message,
            ui_context=req.ui_context, session_id=req.session_id,
            active_agent=req.active_agent,
        )
        return {"response": response_text, "user_id": req.user_id}
    except (ValueError, Exception) as e:
        _handle_llm_error(e)


@app.get("/memory/{user_id}")
def get_memory(user_id: str) -> dict:
    snapshot = memory_agent_get_snapshot(user_id)
    return snapshot.model_dump()


@app.put("/memory/{user_id}")
def update_memory(user_id: str, snapshot: BusinessSnapshot) -> dict:
    store = get_memory_store()
    store.set(user_id, snapshot)
    return memory_agent_get_snapshot(user_id).model_dump()


@app.patch("/memory/{user_id}")
def merge_memory(user_id: str, body: dict = Body(...)) -> dict:
    updated = memory_agent_update(user_id, body)
    return updated.model_dump()
