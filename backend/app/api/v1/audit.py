from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_audit_service
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/events")
def get_audit_events(
    limit: int = Query(default=100, ge=1, le=1000),
    service: AuditService = Depends(get_audit_service),
) -> dict:
    items = service.list_events(limit=limit)
    return {"ok": True, "count": len(items), "items": items}


@router.get("/config-history")
def get_audit_config_history(
    limit: int = Query(default=100, ge=1, le=1000),
    service: AuditService = Depends(get_audit_service),
) -> dict:
    items = service.list_config_history(limit=limit)
    return {"ok": True, "count": len(items), "items": items}


@router.get("/executions")
def get_audit_executions(
    limit: int = Query(default=100, ge=1, le=1000),
    service: AuditService = Depends(get_audit_service),
) -> dict:
    items = service.list_executions(limit=limit)
    return {"ok": True, "count": len(items), "items": items}


@router.get("/risk-blocks")
def get_audit_risk_blocks(
    limit: int = Query(default=100, ge=1, le=1000),
    service: AuditService = Depends(get_audit_service),
) -> dict:
    items = service.list_risk_blocks(limit=limit)
    return {"ok": True, "count": len(items), "items": items}


@router.get("/errors")
def get_audit_errors(
    limit: int = Query(default=100, ge=1, le=1000),
    service: AuditService = Depends(get_audit_service),
) -> dict:
    items = service.list_errors(limit=limit)
    return {"ok": True, "count": len(items), "items": items}
