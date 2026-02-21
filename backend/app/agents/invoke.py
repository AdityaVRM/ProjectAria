"""Invoke specialist agents via LLM. Each returns dict (and optional summary)."""
import json
from typing import Any

from app.llm.client import llm_invoke, extract_json_block
from app.prompts.specialists import (
    STRATEGY_PROMPT,
    MARKETING_PROMPT,
    FINANCE_PROMPT,
    OPS_PROMPT,
    TECH_PROMPT,
    RESEARCH_PROMPT,
    CONTENT_PROMPT,
    LEGAL_PROMPT,
    TASK_PROMPT,
)
from app.prompts.safety import UNIVERSAL_AGENT_RULES, HALLUCINATION_PREVENTION


def _system(agent_prompt: str, add_hallucination: bool = False) -> str:
    parts = [agent_prompt, UNIVERSAL_AGENT_RULES]
    if add_hallucination:
        parts.append(HALLUCINATION_PREVENTION)
    return "\n\n".join(parts)


def _user_message(inputs: dict[str, Any]) -> str:
    return "ARIA has sent you the following input. Respond with valid JSON in the format specified in your instructions.\n\n" + json.dumps(inputs, indent=2)


def strategy_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(STRATEGY_PROMPT, add_hallucination=True)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"analysis": out, "recommendations": [], "risks": [], "confidence_level": "medium"}


def marketing_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(MARKETING_PROMPT)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"strategy_summary": out, "channel_recommendations": [], "quick_wins": []}


def finance_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(FINANCE_PROMPT)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"pricing_recommendation": out, "disclaimer": "AI-generated — verify with a financial advisor."}


def ops_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(OPS_PROMPT)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"workflow_design": out, "tool_recommendations": []}


def tech_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(TECH_PROMPT)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"mvp_scope": [], "architecture_overview": out, "risks": []}


def research_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(RESEARCH_PROMPT, add_hallucination=True)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"key_findings": [out], "confidence": "medium", "recommended_validation_steps": []}


def content_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(CONTENT_PROMPT)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"content": out, "seo_notes": "", "variant_b": ""}


def legal_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(LEGAL_PROMPT)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"guidance": out, "disclaimer": "REQUIRED", "recommended_professional_actions": []}


def task_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    system = _system(TASK_PROMPT)
    user = _user_message(inputs)
    out = llm_invoke(system=system, user_message=user)
    return extract_json_block(out) or {"master_task_list": [], "sprint_plan": {"this_week": [], "next_week": []}, "milestones": [], "blocked_tasks": []}
