"""LangGraph orchestration: load_memory -> classify -> run_agents -> synthesize."""
from typing import Any, Literal, Optional

from langgraph.graph import START, END, StateGraph

from app.orchestration.state import OrchestratorState
from app.orchestration.nodes import (
    load_memory, classify, run_agents, synthesize, onboarding_response,
)


def _route_after_classify(state: OrchestratorState) -> Literal["run_agents", "onboarding"]:
    intent = state.get("intent") or ""
    agent_plan = state.get("agent_plan") or []
    is_new_user = state.get("is_new_user", False)
    if intent == "ONBOARDING" or (is_new_user and not agent_plan):
        return "onboarding"
    return "run_agents"


_graph_compiled = None


def _get_compiled_graph():
    global _graph_compiled
    if _graph_compiled is None:
        graph = StateGraph(OrchestratorState)
        graph.add_node("load_memory", load_memory)
        graph.add_node("classify", classify)
        graph.add_node("run_agents", run_agents)
        graph.add_node("synthesize", synthesize)
        graph.add_node("onboarding", onboarding_response)
        graph.add_edge(START, "load_memory")
        graph.add_edge("load_memory", "classify")
        graph.add_conditional_edges("classify", _route_after_classify, {
            "run_agents": "run_agents",
            "onboarding": "onboarding",
        })
        graph.add_edge("run_agents", "synthesize")
        graph.add_edge("synthesize", END)
        graph.add_edge("onboarding", END)
        _graph_compiled = graph.compile()
    return _graph_compiled


def _run_pipeline(
    user_id: str,
    user_message: str,
    ui_context: str = "chat",
    session_id: Optional[str] = None,
    active_agent: Optional[str] = None,
) -> dict[str, Any]:
    compiled = _get_compiled_graph()
    initial: OrchestratorState = {
        "user_id": user_id,
        "user_message": user_message,
        "ui_context": ui_context,
        "session_id": session_id,
        "active_agent": active_agent,
    }
    return dict(compiled.invoke(initial))


def run_orchestrator(
    user_id: str,
    user_message: str,
    ui_context: str = "chat",
    session_id: Optional[str] = None,
    active_agent: Optional[str] = None,
) -> str:
    result = _run_pipeline(user_id, user_message, ui_context, session_id, active_agent)
    return result.get("final_response") or "I couldn't generate a response. Please try again."


def run_orchestrator_structured(
    user_id: str,
    user_message: str,
    ui_context: str = "chat",
) -> dict[str, Any]:
    result = _run_pipeline(user_id, user_message, ui_context)
    return {
        "final_response": result.get("final_response", ""),
        "intent": result.get("intent", ""),
        "agent_outputs": result.get("agent_outputs") or {},
        "agent_plan": result.get("agent_plan") or [],
        "is_new_user": result.get("is_new_user", False),
    }
