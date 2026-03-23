from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_execution_engine_service
from app.domain.enums import RunMode
from app.services.execution_engine import ExecutionEngineService

router = APIRouter(prefix="/api/trading", tags=["trading"])


class TradingModeUpdateRequest(BaseModel):
    mode: RunMode
    actor: str = "web-user"


class ExecutionPlanCreateRequest(BaseModel):
    strategy_id: str
    mode: RunMode = RunMode.DRY_RUN
    quantity: int = Field(default=1, ge=1)
    max_slippage: float = Field(default=0.003, ge=0)
    max_retries: int = Field(default=2, ge=0, le=10)
    timeout_seconds: int = Field(default=20, ge=1, le=300)
    fallback_market: bool = False
    actor: str = "web-user"
    payload: dict[str, Any] = Field(default_factory=dict)


class ExecutionPlanCancelRequest(BaseModel):
    reason: str | None = None


@router.get("/mode")
def get_trading_mode(service: ExecutionEngineService = Depends(get_execution_engine_service)) -> dict:
    return {"ok": True, "data": service.get_current_mode()}


@router.put("/mode")
def set_trading_mode(
    body: TradingModeUpdateRequest,
    service: ExecutionEngineService = Depends(get_execution_engine_service),
) -> dict:
    try:
        data = service.set_current_mode(body.mode, actor=body.actor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "data": data}


@router.post("/execution/plans")
def create_execution_plan(
    body: ExecutionPlanCreateRequest,
    service: ExecutionEngineService = Depends(get_execution_engine_service),
) -> dict:
    try:
        data = service.create_execution_plan(
            strategy_id=body.strategy_id,
            mode=body.mode,
            quantity=body.quantity,
            max_slippage=body.max_slippage,
            max_retries=body.max_retries,
            timeout_seconds=body.timeout_seconds,
            fallback_market=body.fallback_market,
            actor=body.actor,
            payload=body.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "data": data}


@router.post("/execution/plans/{plan_id}/confirm")
def confirm_execution_plan(
    plan_id: str,
    service: ExecutionEngineService = Depends(get_execution_engine_service),
) -> dict:
    data = service.confirm_plan(plan_id)
    if not data:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"ok": True, "data": data}


@router.post("/execution/plans/{plan_id}/cancel")
def cancel_execution_plan(
    plan_id: str,
    body: ExecutionPlanCancelRequest,
    service: ExecutionEngineService = Depends(get_execution_engine_service),
) -> dict:
    data = service.cancel_plan(plan_id, reason=body.reason)
    if not data:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"ok": True, "data": data}


@router.get("/execution/monitor")
def execution_monitor(service: ExecutionEngineService = Depends(get_execution_engine_service)) -> dict:
    return {"ok": True, "data": service.monitor()}
