"""SoloOS Backend — FastAPI app and routes."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import ChatRequest, BusinessSnapshot
from app.orchestration import run_orchestrator
from app.memory import get_memory_store, memory_agent_get_snapshot, memory_agent_update


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Shutdown: close DB pools etc. if needed


app = FastAPI(
    title="SoloOS — Agentic OS",
    description="Multi-Agent Orchestration Platform for Solopreneurs",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "solos-api"}


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    """Single turn: run orchestration and return ARIA's response."""
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
    if req.active_agent and message.startswith(f"[Agent Studio - {req.active_agent}]"):
        message = message.split("\n", 1)[-1].strip() or message
    try:
        response_text = run_orchestrator(
            user_id=req.user_id,
            user_message=message,
            ui_context=req.ui_context,
            session_id=req.session_id,
            active_agent=req.active_agent,
        )
        return {"response": response_text, "user_id": req.user_id}
    except ValueError as e:
        if "API key" in str(e) or "CURSOR_COMPOSER" in str(e) or "ANTHROPIC" in str(e):
            raise HTTPException(status_code=503, detail="LLM not configured")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{user_id}")
def get_memory(user_id: str) -> dict:
    """Get business snapshot for user (MEMORY_AGENT.get_snapshot)."""
    snapshot = memory_agent_get_snapshot(user_id)
    return snapshot.model_dump()


@app.put("/memory/{user_id}")
def update_memory(user_id: str, snapshot: BusinessSnapshot) -> dict:
    """Update business snapshot (ARIA instructs MEMORY_AGENT to merge)."""
    store = get_memory_store()
    store.set(user_id, snapshot)
    return memory_agent_get_snapshot(user_id).model_dump()


@app.patch("/memory/{user_id}")
def merge_memory(user_id: str, body: dict = Body(...)) -> dict:
    """Merge updates into snapshot (partial update)."""
    updated = memory_agent_update(user_id, body)
    return updated.model_dump()
