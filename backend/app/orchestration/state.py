"""Orchestration state — passed through the LangGraph pipeline."""
from typing import Any, TypedDict


class OrchestratorState(TypedDict, total=False):
    user_id: str
    user_message: str
    ui_context: str
    session_id: str | None
    active_agent: str | None  # When set (e.g. Agent Studio), force single-agent dispatch
    # From MEMORY_AGENT
    snapshot: dict[str, Any]  # BusinessSnapshot as dict
    is_new_user: bool
    # From classifier
    intent: str
    agent_plan: list[dict[str, Any]]  # [{"agent": "STRATEGY_AGENT", "inputs": {...}}, ...]; parallel: list of lists
    # After running agents
    agent_outputs: dict[str, Any]  # agent_name -> output dict
    # Final
    final_response: str
    error: str
