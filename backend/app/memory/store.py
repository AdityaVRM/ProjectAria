"""In-memory store for business snapshots (MEMORY_AGENT backend)."""
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel

from app.schemas import BusinessSnapshot

_store_instance: Optional["MemoryStore"] = None


class MemoryStore:
    def __init__(self) -> None:
        self._data: dict[str, BusinessSnapshot] = {}

    def get(self, user_id: str) -> Optional[BusinessSnapshot]:
        return self._data.get(user_id)

    def set(self, user_id: str, snapshot: BusinessSnapshot) -> None:
        snapshot.last_updated = datetime.now(timezone.utc).isoformat()
        snapshot.user_id = user_id
        self._data[user_id] = snapshot

    def merge(self, user_id: str, updates: dict) -> BusinessSnapshot:
        existing = self.get(user_id)
        base = existing.model_copy(deep=True) if existing else BusinessSnapshot(user_id=user_id)
        for key, value in updates.items():
            if not hasattr(base, key) or value is None:
                continue
            current = getattr(base, key)
            if isinstance(current, BaseModel) and isinstance(value, dict):
                for sub_k, sub_v in value.items():
                    if hasattr(current, sub_k) and sub_v is not None:
                        setattr(current, sub_k, sub_v)
            else:
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
