from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_market_cache_service, get_market_data_service
from app.domain.enums import ExchangeName
from app.services.market_cache import MarketCacheService
from app.services.market_data import MarketDataService

router = APIRouter(prefix="/api/options", tags=["options"])


@router.get("/chain")
async def get_option_chain(
    exchange: ExchangeName = ExchangeName.BINANCE,
    expiry: date | None = Query(default=None),
    limit: int = Query(default=300, ge=1, le=2000),
    service: MarketDataService = Depends(get_market_data_service),
    cache: MarketCacheService = Depends(get_market_cache_service),
) -> dict:
    chain = await service.get_option_chain(exchange=exchange, expiry=expiry)
    rows = [
        {
            "symbol": q.contract.symbol,
            "expiry": q.contract.expiry.isoformat(),
            "strike": q.contract.strike,
            "option_type": q.contract.option_type.value,
            "bid": q.bid,
            "ask": q.ask,
            "mark": q.mark,
            "iv": q.iv,
            "distance_fields_note": "Distance to spot is computed in strategy endpoints.",
        }
        for q in chain[:limit]
    ]
    cache.update_chain(rows)
    return {
        "ok": True,
        "exchange": exchange.value,
        "expiry": expiry.isoformat() if expiry else None,
        "count": len(chain),
        "items": rows,
    }


@router.get("/realtime-chain")
def get_realtime_chain(
    limit: int = Query(default=300, ge=1, le=2000),
    cache: MarketCacheService = Depends(get_market_cache_service),
) -> dict:
    data = cache.latest_chain(limit=limit)
    return {"ok": True, "data": data}
