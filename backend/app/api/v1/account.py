from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_account_service
from app.domain.enums import ExchangeName
from app.services.account_service import AccountService

router = APIRouter(prefix="/api/account", tags=["account"])


@router.get("/summary")
async def account_summary(
    exchange: ExchangeName = ExchangeName.BINANCE,
    refresh: bool = Query(default=False),
    service: AccountService = Depends(get_account_service),
) -> dict:
    data = await service.refresh_summary(exchange) if refresh else service.get_summary(exchange)
    return {"ok": True, "data": data}


@router.get("/risk")
async def account_risk(
    exchange: ExchangeName = ExchangeName.BINANCE,
    service: AccountService = Depends(get_account_service),
) -> dict:
    return {"ok": True, "data": service.get_risk(exchange)}


@router.get("/positions")
async def account_positions(
    exchange: ExchangeName = ExchangeName.BINANCE,
    service: AccountService = Depends(get_account_service),
) -> dict:
    return {"ok": True, "data": service.get_positions_snapshot(exchange)}


@router.get("/pnl")
async def account_pnl(
    exchange: ExchangeName = ExchangeName.BINANCE,
    service: AccountService = Depends(get_account_service),
) -> dict:
    return {"ok": True, "data": service.get_pnl(exchange)}


@router.get("/margin")
async def account_margin(
    exchange: ExchangeName = ExchangeName.BINANCE,
    service: AccountService = Depends(get_account_service),
) -> dict:
    return {"ok": True, "data": service.get_margin(exchange)}
