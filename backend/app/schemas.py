"""Shared Pydantic schemas for SoloOS."""
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class AgentOutputsSummary(BaseModel):
    strategy: str = ""
    marketing: str = ""
    finance: str = ""
    tech: str = ""
    research: str = ""
    content: str = ""
    legal: str = ""
    ops: str = ""


class BusinessSnapshot(BaseModel):
    user_id: str = ""
    business_name: str = ""
    one_liner: str = ""
    stage: Literal["idea", "validation", "pre-revenue", "revenue", "scaling"] = "idea"
    industry: str = ""
    target_customer: str = ""
    current_mrr: str = ""
    primary_goal_90_days: str = ""
    completed_milestones: list[str] = Field(default_factory=list)
    active_projects: list[str] = Field(default_factory=list)
    pending_tasks: list[str] = Field(default_factory=list)
    key_decisions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    agent_outputs_summary: AgentOutputsSummary = Field(default_factory=AgentOutputsSummary)
    last_updated: str = ""
    capacity_hours_per_week: str = ""


IntentType = Literal[
    "NEW_IDEA", "EXISTING_PROBLEM", "TASK_REQUEST",
    "PROGRESS_UPDATE", "QUESTION", "PIVOT",
]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    ui_context: Literal["chat", "dashboard", "agent_studio"] = "chat"
    active_agent: Optional[str] = None


class RunRequest(BaseModel):
    message: str
    user_id: str


class IterateRequest(BaseModel):
    user_id: str
    agent_name: str
    feedback: str
    original_message: str = ""
    previous_output: dict[str, Any] = Field(default_factory=dict)
    iteration: int = 1


class TaskItem(BaseModel):
    task: str
    priority: Literal["P1", "P2", "P3"]
    effort: Literal["small", "medium", "large"]
    impact: Literal["high", "medium", "low"]
    deadline: str = ""
    dependencies: list[str] = Field(default_factory=list)
    assigned_to: str = "founder"


class TaskAgentOutput(BaseModel):
    master_task_list: list[TaskItem] = Field(default_factory=list)
    sprint_plan: dict[str, list[str]] = Field(default_factory=dict)
    milestones: list[str] = Field(default_factory=list)
    blocked_tasks: list[str] = Field(default_factory=list)


class AgentInput(BaseModel):
    business_context: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    raw: dict[str, Any]
    summary: str = ""
    agent_name: str = ""
