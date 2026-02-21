"""MEMORY_AGENT: get_snapshot and update. Uses store; optionally calls LLM to parse/merge."""
from app.schemas import BusinessSnapshot
from app.memory.store import get_memory_store


def memory_agent_get_snapshot(user_id: str) -> BusinessSnapshot:
    store = get_memory_store()
    snapshot = store.get(user_id)
    if snapshot is None:
        snapshot = BusinessSnapshot(
            user_id=user_id,
            last_updated="",
        )
        # Flag for orchestrator: onboarding required
    return snapshot


def memory_agent_update(
    user_id: str,
    updates: dict,
) -> BusinessSnapshot:
    """Merge ARIA's update brief into the business snapshot. No LLM required for basic merge."""
    store = get_memory_store()
    return store.merge(user_id, updates)
