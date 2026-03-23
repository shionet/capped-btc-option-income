from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_pnl_service
from app.services.pnl_service import PnlService

router = APIRouter(prefix="/api/pnl", tags=["pnl"])


@router.get("/summary")
def pnl_summary(service: PnlService = Depends(get_pnl_service)) -> dict:
    return {"ok": True, "data": service.summary()}


@router.get("/history")
def pnl_history(
    limit: int = Query(default=120, ge=1, le=1000),
    service: PnlService = Depends(get_pnl_service),
) -> dict:
    items = service.history(limit=limit)
    return {"ok": True, "count": len(items), "items": items}


@router.get("/by-strategy")
def pnl_by_strategy(service: PnlService = Depends(get_pnl_service)) -> dict:
    items = service.by_strategy()
    return {"ok": True, "count": len(items), "items": items}
