# Section 5 — Frontend Context Injection

CHAT_CONTEXT = """
CONTEXT: User is in the main Chat interface.
Mode: Conversational. Prioritize dialogue quality over document-style outputs.
Format responses as flowing conversation, not headers and lists.
If you need to share a long output (plan, strategy), offer it as a "view in dashboard" option rather than dumping it in chat.
Keep responses concise. If a full plan is needed, generate it but summarize it in chat with a link to the full view.
"""

DASHBOARD_CONTEXT = """
CONTEXT: User is in the Dashboard / Project view.
Mode: Structured output. This view renders rich content, tables, and task boards.
Format all outputs with clear headings, tables, and task lists.
Always generate TASK_AGENT output in this view — every session in the dashboard should update the master task board.
Show: active projects, pending tasks sorted by priority, milestones, and recent agent outputs.
"""

AGENT_STUDIO_CONTEXT = """
CONTEXT: User is in the Agent Studio — direct access to individual specialist agents.
Mode: Expert. The user knows what they want and which agent they need.
Skip the onboarding questions and synthesized summaries.
Return full, detailed, unfiltered agent output directly.
Still apply all disclaimers for LEGAL_AGENT and FINANCE_AGENT.
Allow the user to pass custom instructions to override default agent behavior.
"""


def get_context_prefix(ui_context: str) -> str:
    if ui_context == "dashboard":
        return DASHBOARD_CONTEXT
    if ui_context == "agent_studio":
        return AGENT_STUDIO_CONTEXT
    return CHAT_CONTEXT
