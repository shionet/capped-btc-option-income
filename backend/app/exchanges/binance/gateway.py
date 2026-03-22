from __future__ import annotations

from datetime import date, datetime, timezone

from app.domain.enums import ExchangeName
from app.domain.models import OptionQuote, UnderlyingQuote
from app.exchanges.base import ExchangeGateway
from app.exchanges.binance.client import BinanceRestClient
from app.exchanges.binance.mapper import map_option_chain


def _safe_float(value: str | float | int | None) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


class BinanceGateway(ExchangeGateway):
    def __init__(self, client: BinanceRestClient) -> None:
        self.client = client

    async def get_underlying_quote(self, symbol: str) -> UnderlyingQuote:
        ticker = await self.client.get_spot_ticker_price(symbol)
        return UnderlyingQuote(
            exchange=ExchangeName.BINANCE,
            symbol=symbol,
            price=_safe_float(ticker.get("price")),
            mark_price=_safe_float(ticker.get("price")),
            timestamp=datetime.now(timezone.utc),
        )

    async def get_option_chain(self, underlying: str, expiry: date | None = None) -> list[OptionQuote]:
        exchange_info = await self.client.get_options_exchange_info()
        ticker_rows = await self.client.get_options_ticker()
        mark_rows = await self.client.get_options_mark()
        return map_option_chain(
            exchange_info=exchange_info,
            ticker_rows=ticker_rows,
            mark_rows=mark_rows,
            underlying=underlying,
            expiry=expiry,
        )
