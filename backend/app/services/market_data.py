from __future__ import annotations

from datetime import date

from app.core.constants import BTC_SYMBOL
from app.domain.enums import ExchangeName
from app.domain.models import OptionQuote, UnderlyingQuote
from app.exchanges.factory import build_exchange_gateway
from app.core.config import Settings


class MarketDataService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def get_btc_quote(self, exchange: ExchangeName = ExchangeName.BINANCE) -> UnderlyingQuote:
        gateway = build_exchange_gateway(exchange, self.settings)
        return await gateway.get_underlying_quote(BTC_SYMBOL)

    async def get_option_chain(
        self,
        *,
        exchange: ExchangeName = ExchangeName.BINANCE,
        underlying: str = BTC_SYMBOL,
        expiry: date | None = None,
    ) -> list[OptionQuote]:
        gateway = build_exchange_gateway(exchange, self.settings)
        return await gateway.get_option_chain(underlying, expiry=expiry)
