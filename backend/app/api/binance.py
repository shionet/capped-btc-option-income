from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.exchanges.binance.client import (
    BinanceAuthError,
    BinanceRequestError,
    BinanceRestClient,
)

router = APIRouter(prefix="/api/binance", tags=["binance"])


def get_binance_client(settings: Settings = Depends(get_settings)) -> BinanceRestClient:
    return BinanceRestClient(
        base_url=settings.binance_base_url,
        options_base_url=settings.binance_options_base_url,
        timeout_seconds=settings.binance_timeout_seconds,
        recv_window=settings.binance_recv_window,
        api_key=settings.binance_api_key,
        api_secret=settings.binance_api_secret,
    )


@router.get("/ping")
async def ping_binance(client: BinanceRestClient = Depends(get_binance_client)) -> dict:
    try:
        data = await client.get_server_time()
        return {"ok": True, "server_time": data.get("serverTime"), "raw": data}
    except BinanceRequestError as exc:
        raise HTTPException(status_code=502, detail={"message": str(exc), "payload": exc.payload}) from exc


@router.get("/account/spot")
async def get_spot_account(client: BinanceRestClient = Depends(get_binance_client)) -> dict:
    try:
        data = await client.get_spot_account_info()
        non_zero_balances = [
            b for b in data.get("balances", []) if float(b.get("free", 0)) > 0 or float(b.get("locked", 0)) > 0
        ]
        return {
            "ok": True,
            "account_type": data.get("accountType"),
            "can_trade": data.get("canTrade"),
            "update_time": data.get("updateTime"),
            "balances_non_zero": non_zero_balances,
            "raw": data,
        }
    except BinanceAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except BinanceRequestError as exc:
        raise HTTPException(status_code=502, detail={"message": str(exc), "payload": exc.payload}) from exc


@router.get("/account/spot/api-restrictions")
async def get_spot_api_restrictions(client: BinanceRestClient = Depends(get_binance_client)) -> dict:
    try:
        data = await client.get_spot_api_restrictions()
        return {"ok": True, "raw": data}
    except BinanceAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except BinanceRequestError as exc:
        raise HTTPException(status_code=502, detail={"message": str(exc), "payload": exc.payload}) from exc


@router.get("/account/options")
async def get_options_account(client: BinanceRestClient = Depends(get_binance_client)) -> dict:
    try:
        data = await client.get_options_account_info()
        return {"ok": True, "raw": data}
    except BinanceAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except BinanceRequestError as exc:
        raise HTTPException(status_code=502, detail={"message": str(exc), "payload": exc.payload}) from exc
