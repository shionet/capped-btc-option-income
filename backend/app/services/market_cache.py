from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any


@dataclass
class MarketCacheState:
    quote: dict[str, Any] = field(default_factory=dict)
    chain: list[dict[str, Any]] = field(default_factory=list)
    last_quote_at: datetime | None = None
    last_chain_at: datetime | None = None
    ws_connected: bool = False
    exchange_connected: bool = False


class MarketCacheService:
    def __init__(self) -> None:
        self._state = MarketCacheState()
        self._lock = Lock()

    def update_quote(self, quote: dict[str, Any]) -> None:
        with self._lock:
            self._state.quote = quote
            self._state.last_quote_at = datetime.now(timezone.utc)
            self._state.exchange_connected = True

    def update_chain(self, chain: list[dict[str, Any]]) -> None:
        with self._lock:
            self._state.chain = chain
            self._state.last_chain_at = datetime.now(timezone.utc)
            self._state.exchange_connected = True

    def update_stream_connected(self, connected: bool) -> None:
        with self._lock:
            self._state.ws_connected = connected

    def stream_status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "ws_connected": self._state.ws_connected,
                "exchange_connected": self._state.exchange_connected,
                "last_quote_at": self._state.last_quote_at.isoformat() if self._state.last_quote_at else None,
                "last_chain_at": self._state.last_chain_at.isoformat() if self._state.last_chain_at else None,
            }

    def latest_quote(self) -> dict[str, Any]:
        with self._lock:
            return {
                "quote": self._state.quote,
                "updated_at": self._state.last_quote_at.isoformat() if self._state.last_quote_at else None,
            }

    def latest_chain(self, limit: int = 200) -> dict[str, Any]:
        with self._lock:
            return {
                "items": self._state.chain[:limit],
                "count": len(self._state.chain),
                "updated_at": self._state.last_chain_at.isoformat() if self._state.last_chain_at else None,
            }
