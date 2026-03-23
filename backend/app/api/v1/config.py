from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_config_service
from app.domain.enums import ConfigDomain
from app.services.config_service import ConfigService

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdatePayload(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)
    publish: bool = True
    actor: str = "web-user"
    reason: str | None = None


@router.get("/strategy")
def get_strategy_config(service: ConfigService = Depends(get_config_service)) -> dict:
    return {"ok": True, "data": service.get_config(ConfigDomain.STRATEGY)}


@router.put("/strategy")
def put_strategy_config(body: ConfigUpdatePayload, service: ConfigService = Depends(get_config_service)) -> dict:
    data = service.update_config(
        domain=ConfigDomain.STRATEGY,
        payload=body.payload,
        publish=body.publish,
        actor=body.actor,
        reason=body.reason,
    )
    return {"ok": True, "data": data}


@router.get("/risk")
def get_risk_config(service: ConfigService = Depends(get_config_service)) -> dict:
    return {"ok": True, "data": service.get_config(ConfigDomain.RISK)}


@router.put("/risk")
def put_risk_config(body: ConfigUpdatePayload, service: ConfigService = Depends(get_config_service)) -> dict:
    data = service.update_config(
        domain=ConfigDomain.RISK,
        payload=body.payload,
        publish=body.publish,
        actor=body.actor,
        reason=body.reason,
    )
    return {"ok": True, "data": data}


@router.get("/execution")
def get_execution_config(service: ConfigService = Depends(get_config_service)) -> dict:
    return {"ok": True, "data": service.get_config(ConfigDomain.EXECUTION)}


@router.put("/execution")
def put_execution_config(body: ConfigUpdatePayload, service: ConfigService = Depends(get_config_service)) -> dict:
    data = service.update_config(
        domain=ConfigDomain.EXECUTION,
        payload=body.payload,
        publish=body.publish,
        actor=body.actor,
        reason=body.reason,
    )
    return {"ok": True, "data": data}
