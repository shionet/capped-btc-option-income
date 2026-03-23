from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import RunMode


class TradingModeState(BaseModel):
    mode: RunMode
    live_trading_enabled: bool
    execution_config_version: int
    updated_at: datetime | None = None


class ExecutionPlan(BaseModel):
    plan_id: str
    strategy_id: str | None = None
    mode: RunMode
    status: str
    quantity: int = Field(ge=1)
    max_slippage: float
    max_retries: int
    timeout_seconds: int
    fallback_market: bool
    error_message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_by: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
