"""LangGraph orchestration: load_memory -> classify -> run_agents -> synthesize."""
from typing import Literal

from langgraph.graph import START, END, StateGraph

from app.orchestration.state import OrchestratorState
from app.orchestration.nodes import (
    load_memory,
    classify,
    run_agents,
    synthesize,
    onboarding_response,
)


def _route_after_classify(state: OrchestratorState) -> Literal["run_agents", "onboarding"]:
    intent = state.get("intent") or ""
    agent_plan = state.get("agent_plan") or []
    is_new_user = state.get("is_new_user", False)
    if intent == "ONBOARDING" or (is_new_user and not agent_plan):
        return "onboarding"
    return "run_agents"


def build_graph() -> StateGraph:
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

    return graph


def run_orchestrator(
    user_id: str,
    user_message: str,
    ui_context: str = "chat",
    session_id: str | None = None,
    active_agent: str | None = None,
) -> str:
    """Run the full orchestration and return the final response text."""
    graph = build_graph().compile()
    initial: OrchestratorState = {
        "user_id": user_id,
        "user_message": user_message,
        "ui_context": ui_context,
        "session_id": session_id,
        "active_agent": active_agent,
    }
    result = graph.invoke(initial)
    return result.get("final_response") or "I couldn't generate a response. Please try again."
