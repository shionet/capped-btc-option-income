from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_market_cache_service, get_market_data_service
from app.domain.enums import ExchangeName
from app.services.market_cache import MarketCacheService
from app.services.market_data import MarketDataService

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/btc")
async def get_btc_market(
    exchange: ExchangeName = ExchangeName.BINANCE,
    service: MarketDataService = Depends(get_market_data_service),
    cache: MarketCacheService = Depends(get_market_cache_service),
) -> dict:
    quote = await service.get_btc_quote(exchange=exchange)
    chain = await service.get_option_chain(exchange=exchange)
    iv_values = [q.iv for q in chain if q.iv is not None and q.iv > 0]
    iv_status = sum(iv_values) / len(iv_values) if iv_values else None
    payload = {
        "exchange": exchange.value,
        "symbol": quote.symbol,
        "price": quote.price,
        "mark_price": quote.mark_price,
        "timestamp": quote.timestamp.isoformat(),
        "iv_status_proxy": iv_status,
    }
    cache.update_quote(payload)
    cache.update_chain(
        [
            {
                "symbol": q.contract.symbol,
                "expiry": q.contract.expiry.isoformat(),
                "strike": q.contract.strike,
                "option_type": q.contract.option_type.value,
                "bid": q.bid,
                "ask": q.ask,
                "mark": q.mark,
                "iv": q.iv,
            }
            for q in chain[:500]
        ]
    )
    cache.update_stream_connected(True)
    return {
        "ok": True,
        **payload,
        "system_status": "running",
    }


@router.get("/stream-status")
def stream_status(cache: MarketCacheService = Depends(get_market_cache_service)) -> dict:
    return {"ok": True, "data": cache.stream_status()}


@router.get("/quotes/latest")
def latest_quote(cache: MarketCacheService = Depends(get_market_cache_service)) -> dict:
    return {"ok": True, "data": cache.latest_quote()}
