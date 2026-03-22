from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_market_data_service
from app.domain.enums import ExchangeName
from app.services.market_data import MarketDataService

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/btc")
async def get_btc_market(
    exchange: ExchangeName = ExchangeName.BINANCE,
    service: MarketDataService = Depends(get_market_data_service),
) -> dict:
    quote = await service.get_btc_quote(exchange=exchange)
    chain = await service.get_option_chain(exchange=exchange)
    iv_values = [q.iv for q in chain if q.iv is not None and q.iv > 0]
    iv_status = sum(iv_values) / len(iv_values) if iv_values else None
    return {
        "ok": True,
        "exchange": exchange.value,
        "symbol": quote.symbol,
        "price": quote.price,
        "mark_price": quote.mark_price,
        "timestamp": quote.timestamp.isoformat(),
        "iv_status_proxy": iv_status,
        "system_status": "running",
    }
