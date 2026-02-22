"""Orchestration state — passed through the LangGraph pipeline."""
from typing import Any, Optional, TypedDict


class OrchestratorState(TypedDict, total=False):
    user_id: str
    user_message: str
    ui_context: str
    session_id: Optional[str]
    active_agent: Optional[str]
    snapshot: dict[str, Any]
    is_new_user: bool
    intent: str
    agent_plan: list[list[str]]
    agent_outputs: dict[str, Any]
    final_response: str
    error: str
