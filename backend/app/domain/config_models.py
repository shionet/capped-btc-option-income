from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EffectiveConfig(BaseModel):
    domain: str
    version: int
    status: str
    source: str
    effective_at: datetime | None = None
    updated_at: datetime | None = None
    payload: dict[str, Any]


class ConfigChangeHistoryItem(BaseModel):
    id: int
    domain: str
    old_version: int | None = None
    new_version: int
    actor: str
    reason: str | None = None
    diff: dict[str, Any]
    created_at: datetime | None = None
