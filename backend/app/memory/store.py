"""In-memory and persistent store for business snapshots (MEMORY_AGENT backend)."""
from datetime import datetime, timezone
from typing import Optional
from app.schemas import BusinessSnapshot

# In-memory store (per process). Replace with DB/vector store for production.
_store: dict[str, BusinessSnapshot] = {}
_store_instance: Optional["MemoryStore"] = None


class MemoryStore:
    def __init__(self):
        self._data: dict[str, BusinessSnapshot] = {}

    def get(self, user_id: str) -> Optional[BusinessSnapshot]:
        return self._data.get(user_id)

    def set(self, user_id: str, snapshot: BusinessSnapshot) -> None:
        snapshot.last_updated = datetime.now(timezone.utc).isoformat()
        snapshot.user_id = user_id
        self._data[user_id] = snapshot

    def merge(self, user_id: str, updates: dict) -> BusinessSnapshot:
        existing = self.get(user_id)
        if existing is None:
            base = BusinessSnapshot(user_id=user_id)
        else:
            base = existing.model_copy(deep=True)
        for key, value in updates.items():
            if hasattr(base, key) and value is not None:
                setattr(base, key, value)
        base.last_updated = datetime.now(timezone.utc).isoformat()
        self.set(user_id, base)
        return base

    def list_user_ids(self) -> list[str]:
        return list(self._data.keys())


def get_memory_store() -> MemoryStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = MemoryStore()
    return _store_instance
