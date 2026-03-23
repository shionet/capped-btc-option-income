from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_position_service
from app.services.position_service import PositionService

router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("")
def list_positions(
    limit: int = Query(default=200, ge=1, le=1000),
    service: PositionService = Depends(get_position_service),
) -> dict:
    items = service.list_positions(limit=limit)
    return {"ok": True, "count": len(items), "items": items, "summary": service.portfolio_summary()}


@router.get("/open")
def list_open_positions(service: PositionService = Depends(get_position_service)) -> dict:
    items = service.list_positions(status="open")
    return {"ok": True, "count": len(items), "items": items}


@router.get("/closed")
def list_closed_positions(service: PositionService = Depends(get_position_service)) -> dict:
    items = service.list_positions(status="closed")
    return {"ok": True, "count": len(items), "items": items}


@router.get("/{position_id}")
def get_position(position_id: str, service: PositionService = Depends(get_position_service)) -> dict:
    item = service.get_position(position_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    return {"ok": True, "item": item}


@router.post("/{position_id}/close")
def close_position(
    position_id: str,
    actor: str = Query(default="web-user"),
    service: PositionService = Depends(get_position_service),
) -> dict:
    item = service.close_position(position_id, actor=actor)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    return {"ok": True, "item": item}
