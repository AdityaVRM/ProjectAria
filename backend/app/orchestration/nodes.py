"""Orchestration nodes: load_memory, classify, run_agents, synthesize."""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional

from app.memory import memory_agent_get_snapshot, memory_agent_update
from app.llm.client import llm_invoke, extract_json_block
from app.prompts.aria import ARIA_SYSTEM_PROMPT, ORCHESTRATION_RULES
from app.prompts.context import get_context_prefix
from app.prompts.onboarding import ONBOARDING_PROMPT
from app.agents.invoke import (
    strategy_agent, marketing_agent, finance_agent, ops_agent,
    tech_agent, research_agent, content_agent, legal_agent, task_agent,
)
from app.orchestration.state import OrchestratorState

AGENT_INVOKERS = {
    "STRATEGY_AGENT": strategy_agent,
    "MARKETING_AGENT": marketing_agent,
    "FINANCE_AGENT": finance_agent,
    "OPS_AGENT": ops_agent,
    "TECH_AGENT": tech_agent,
    "RESEARCH_AGENT": research_agent,
    "CONTENT_AGENT": content_agent,
    "LEGAL_AGENT": legal_agent,
    "TASK_AGENT": task_agent,
}


def load_memory(state: OrchestratorState) -> dict[str, Any]:
    user_id = state.get("user_id") or ""
    snapshot = memory_agent_get_snapshot(user_id)
    snapshot_dict = snapshot.model_dump()
    is_new = not snapshot.last_updated and not snapshot.business_name
    return {"snapshot": snapshot_dict, "is_new_user": is_new}


def _build_classifier_prompt(state: OrchestratorState) -> str:
    snapshot = state.get("snapshot") or {}
    user_message = state.get("user_message") or ""
    ui_context = state.get("ui_context") or "chat"
    active_agent = state.get("active_agent")
    context_prefix = get_context_prefix(ui_context)
    force_agent = ""
    if active_agent and active_agent in AGENT_INVOKERS:
        force_agent = (
            f'\nThe user is in Agent Studio and has selected {active_agent}. '
            f'Set "agent_plan" to [["{active_agent}"]] and "intent" to "TASK_REQUEST". '
            f'Do not run onboarding.'
        )
    return f"""{context_prefix}

Current business snapshot (from MEMORY_AGENT):
{json.dumps(snapshot, indent=2)}

User message:
"{user_message}"
{force_agent}

{ORCHESTRATION_RULES}

Based on the user message, classify intent and decide which agents to call. If this is a new user (empty or minimal snapshot) and not in Agent Studio, respond with onboarding flow: set "intent" to "ONBOARDING" and "agent_plan" to [].

Otherwise output a JSON object with:
- "intent": one of NEW_IDEA, EXISTING_PROBLEM, TASK_REQUEST, PROGRESS_UPDATE, QUESTION, PIVOT, ONBOARDING
- "agent_plan": list of "steps". Each step is either one agent name or a list of agent names to run in parallel. Example: [["RESEARCH_AGENT", "STRATEGY_AGENT"], "FINANCE_AGENT", "TASK_AGENT"]. Use only: STRATEGY_AGENT, MARKETING_AGENT, FINANCE_AGENT, OPS_AGENT, TECH_AGENT, RESEARCH_AGENT, CONTENT_AGENT, LEGAL_AGENT, TASK_AGENT.
- "reasoning": one sentence why.

Respond with ONLY the JSON object, no markdown."""


def classify(state: OrchestratorState) -> dict[str, Any]:
    system = ARIA_SYSTEM_PROMPT
    user = _build_classifier_prompt(state)
    out = llm_invoke(system=system, user_message=user, max_tokens=1024)
    data = extract_json_block(out)
    if not data:
        return {"intent": "QUESTION", "agent_plan": [], "error": "Could not parse classifier output"}
    intent = data.get("intent") or "QUESTION"
    raw_plan = data.get("agent_plan") or []
    steps: list[list[str]] = []
    for step in raw_plan:
        if isinstance(step, list):
            steps.append([a for a in step if a in AGENT_INVOKERS])
        elif isinstance(step, str) and step in AGENT_INVOKERS:
            steps.append([step])
    return {"intent": intent, "agent_plan": steps}


def _agent_inputs(
    agent_name: str,
    state: OrchestratorState,
    accumulated_outputs: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    snapshot = state.get("snapshot") or {}
    user_message = state.get("user_message") or ""
    bc = json.dumps({
        "business_name": snapshot.get("business_name"),
        "one_liner": snapshot.get("one_liner"),
        "stage": snapshot.get("stage"),
        "industry": snapshot.get("industry"),
        "target_customer": snapshot.get("target_customer"),
        "primary_goal_90_days": snapshot.get("primary_goal_90_days"),
        "pending_tasks": snapshot.get("pending_tasks", []),
    })
    base: dict[str, Any] = {"business_context": bc}
    if agent_name == "TASK_AGENT":
        prev = accumulated_outputs or state.get("agent_outputs") or {}
        plan_parts = [str(v) for v in prev.values()]
        base["plan_or_output"] = "\n\n".join(plan_parts)
        base["timeframe"] = "90 days"
        base["user_capacity"] = snapshot.get("capacity_hours_per_week") or "10"
        base["existing_tasks"] = snapshot.get("pending_tasks") or []
    else:
        base["specific_question"] = user_message
        base["constraints"] = ""
    return base


def _run_with_quality_check(agent_name: str, invoker: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    """Run an agent; auto-retry once if output lacks substance."""
    result = invoker(inputs)
    if not isinstance(result, dict) or "error" in result:
        return result
    has_substance = any(isinstance(v, (str, list)) and len(v) > 30 for v in result.values())
    if has_substance:
        return result
    retry_inputs = dict(inputs)
    retry_inputs["constraints"] = (
        "Your previous response lacked detail. Provide thorough, specific, "
        "actionable analysis. Previous attempt: " + json.dumps(result)[:2000]
    )
    return invoker(retry_inputs)


def run_agents(state: OrchestratorState) -> dict[str, Any]:
    agent_plan = state.get("agent_plan") or []
    agent_outputs: dict[str, Any] = dict(state.get("agent_outputs") or {})
    for step in agent_plan:
        if not step:
            continue
        if len(step) == 1:
            name = step[0]
            inv = AGENT_INVOKERS.get(name)
            if inv:
                inputs = _agent_inputs(name, state, accumulated_outputs=agent_outputs)
                try:
                    agent_outputs[name] = _run_with_quality_check(name, inv, inputs)
                except Exception as e:
                    agent_outputs[name] = {"error": str(e)}
        else:
            with ThreadPoolExecutor(max_workers=len(step)) as ex:
                futures = {}
                for name in step:
                    inv = AGENT_INVOKERS.get(name)
                    if inv:
                        inputs = _agent_inputs(name, state, accumulated_outputs=agent_outputs)
                        futures[ex.submit(_run_with_quality_check, name, inv, inputs)] = name
                for fut in as_completed(futures):
                    name = futures[fut]
                    try:
                        agent_outputs[name] = fut.result()
                    except Exception as e:
                        agent_outputs[name] = {"error": str(e)}
    return {"agent_outputs": agent_outputs}


def _persist_agent_results(user_id: str, agent_outputs: dict[str, Any]) -> None:
    if not user_id or not agent_outputs:
        return
    updates: dict[str, Any] = {}
    summary: dict[str, str] = {}
    for name, output in agent_outputs.items():
        key = name.replace("_AGENT", "").lower()
        if isinstance(output, dict) and "error" not in output:
            for v in output.values():
                if isinstance(v, str) and len(v) > 10:
                    summary[key] = v[:300]
                    break
    if summary:
        updates["agent_outputs_summary"] = summary
    task_output = agent_outputs.get("TASK_AGENT")
    if task_output and isinstance(task_output, dict):
        tasks = task_output.get("master_task_list", [])
        if tasks:
            updates["pending_tasks"] = [
                t.get("task", str(t)) if isinstance(t, dict) else str(t) for t in tasks
            ]
    if updates:
        memory_agent_update(user_id, updates)


def synthesize(state: OrchestratorState) -> dict[str, Any]:
    user_message = state.get("user_message") or ""
    snapshot = state.get("snapshot") or {}
    agent_outputs = state.get("agent_outputs") or {}
    intent = state.get("intent") or ""
    is_new_user = state.get("is_new_user", False)
    ui_context = state.get("ui_context") or "chat"
    context_prefix = get_context_prefix(ui_context)

    system = ARIA_SYSTEM_PROMPT + "\n\n" + context_prefix
    user = f"""You are ARIA. Synthesize the following into a single response for the user.

User message: "{user_message}"
Intent: {intent}
New user: {is_new_user}

Business snapshot (summary): {json.dumps({k: snapshot.get(k) for k in ["business_name", "one_liner", "stage", "primary_goal_90_days"] if snapshot.get(k)}, indent=2)}

Agent outputs (use these to build your response; do not dump raw JSON):
{json.dumps(agent_outputs, indent=2)[:12000]}

Instructions:
- Lead with a 2-3 sentence executive summary.
- Present insights in clearly labeled, digestible sections.
- End with: (a) key decisions made, (b) next 3 priority actions, (c) offer to go deeper.
- Use plain language. If any output is from LEGAL_AGENT or FINANCE_AGENT, include the disclaimer that this is AI-generated guidance, not professional advice.
"""
    try:
        final = llm_invoke(system=system, user_message=user, max_tokens=4096)
    except Exception as e:
        final = f"I ran into an issue while synthesizing: {e}. Please try rephrasing or try again."

    _persist_agent_results(state.get("user_id") or "", agent_outputs)
    return {"final_response": final}


def _extract_onboarding_data(user_message: str) -> dict[str, Any]:
    system = (
        "Extract any business information from the user's message. "
        "Return a JSON object with only the fields you can confidently extract. "
        "Possible fields: business_name, one_liner, stage (one of: idea, validation, "
        "pre-revenue, revenue, scaling), industry, target_customer, "
        "primary_goal_90_days, capacity_hours_per_week. "
        "Return {} if no business info is found. Respond with ONLY the JSON object."
    )
    try:
        out = llm_invoke(system=system, user_message=user_message, max_tokens=512)
        return extract_json_block(out) or {}
    except Exception:
        return {}


def onboarding_response(state: OrchestratorState) -> dict[str, Any]:
    user_message = state.get("user_message") or ""
    snapshot = state.get("snapshot") or {}
    system = ARIA_SYSTEM_PROMPT + "\n\n" + ONBOARDING_PROMPT
    user = f"""Current (possibly empty) business snapshot: {json.dumps(snapshot, indent=2)}

User just said: "{user_message}"

Respond as ARIA in onboarding mode: warm, one question at a time. Extract what you can from their message and ask the single next best question to fill the onboarding flow. Do not output JSON."""
    try:
        final = llm_invoke(system=system, user_message=user, max_tokens=1024)
    except Exception as e:
        final = f"Welcome to SoloOS! I'm ARIA. What are you working on? (Error: {e})"

    user_id = state.get("user_id") or ""
    if user_id and user_message.strip():
        extracted = _extract_onboarding_data(user_message)
        if extracted:
            memory_agent_update(user_id, extracted)

    return {"final_response": final}
