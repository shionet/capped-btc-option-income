from __future__ import annotations

from datetime import date

from app.domain.models import OptionQuote, UnderlyingQuote
from app.exchanges.base import ExchangeGateway


class OkxGateway(ExchangeGateway):
    async def get_underlying_quote(self, symbol: str) -> UnderlyingQuote:
        raise NotImplementedError("OKX adapter is reserved for phase 2.")

    async def get_option_chain(self, underlying: str, expiry: date | None = None) -> list[OptionQuote]:
        raise NotImplementedError("OKX adapter is reserved for phase 2.")
