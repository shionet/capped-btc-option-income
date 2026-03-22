from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.domain.models import OptionQuote, UnderlyingQuote


class ExchangeGateway(ABC):
    @abstractmethod
    async def get_underlying_quote(self, symbol: str) -> UnderlyingQuote:
        raise NotImplementedError

    @abstractmethod
    async def get_option_chain(self, underlying: str, expiry: date | None = None) -> list[OptionQuote]:
        raise NotImplementedError
