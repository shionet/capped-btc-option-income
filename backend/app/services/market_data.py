from __future__ import annotations

from datetime import date
import time

from app.core.constants import BTC_SYMBOL
from app.domain.enums import ExchangeName
from app.domain.models import OptionQuote, UnderlyingQuote
from app.exchanges.binance.client import BinanceRequestError
from app.exchanges.factory import build_exchange_gateway
from app.core.config import Settings


class MarketDataService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._quote_cache: dict[str, tuple[float, UnderlyingQuote]] = {}
        self._chain_cache: dict[str, tuple[float, list[OptionQuote]]] = {}
        self._quote_ttl_seconds = 2.0
        self._chain_ttl_seconds = 8.0

    def _build_chain_key(self, exchange: ExchangeName, underlying: str, expiry: date | None) -> str:
        return f"{exchange.value}:{underlying}:{expiry.isoformat() if expiry else 'all'}"

    async def get_btc_quote(self, exchange: ExchangeName = ExchangeName.BINANCE) -> UnderlyingQuote:
        key = exchange.value
        cached = self._quote_cache.get(key)
        now = time.time()
        if cached and now - cached[0] <= self._quote_ttl_seconds:
            return cached[1]
        gateway = build_exchange_gateway(exchange, self.settings)
        try:
            quote = await gateway.get_underlying_quote(BTC_SYMBOL)
            self._quote_cache[key] = (now, quote)
            return quote
        except BinanceRequestError:
            if cached:
                return cached[1]
            raise

    async def get_option_chain(
        self,
        *,
        exchange: ExchangeName = ExchangeName.BINANCE,
        underlying: str = BTC_SYMBOL,
        expiry: date | None = None,
    ) -> list[OptionQuote]:
        cache_key = self._build_chain_key(exchange, underlying, expiry)
        cached = self._chain_cache.get(cache_key)
        now = time.time()
        if cached and now - cached[0] <= self._chain_ttl_seconds:
            return cached[1]
        gateway = build_exchange_gateway(exchange, self.settings)
        try:
            chain = await gateway.get_option_chain(underlying, expiry=expiry)
            self._chain_cache[cache_key] = (now, chain)
            return chain
        except BinanceRequestError:
            if cached:
                return cached[1]
            raise
