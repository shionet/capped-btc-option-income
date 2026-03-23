from typing import Dict, Tuple

from app.core.config import Settings
from app.core.exceptions import UnsupportedExchangeError
from app.domain.enums import ExchangeName
from app.exchanges.base import ExchangeGateway
from app.exchanges.binance.client import BinanceRestClient
from app.exchanges.binance.gateway import BinanceGateway
from app.exchanges.okx.gateway import OkxGateway

_BINANCE_GATEWAY_CACHE: Dict[Tuple[str, str, int, int, int, str, str], BinanceGateway] = {}


def build_exchange_gateway(exchange: ExchangeName, settings: Settings) -> ExchangeGateway:
    if exchange == ExchangeName.BINANCE:
        cache_key = (
            settings.binance_base_url,
            settings.binance_options_base_url,
            settings.binance_timeout_seconds,
            settings.binance_recv_window,
            settings.binance_exchange_info_cache_ttl_seconds,
            settings.binance_api_key or "",
            settings.binance_api_secret or "",
        )
        cached = _BINANCE_GATEWAY_CACHE.get(cache_key)
        if cached:
            return cached
        client = BinanceRestClient(
            base_url=settings.binance_base_url,
            options_base_url=settings.binance_options_base_url,
            timeout_seconds=settings.binance_timeout_seconds,
            recv_window=settings.binance_recv_window,
            exchange_info_cache_ttl_seconds=settings.binance_exchange_info_cache_ttl_seconds,
            api_key=settings.binance_api_key,
            api_secret=settings.binance_api_secret,
        )
        gateway = BinanceGateway(client)
        _BINANCE_GATEWAY_CACHE[cache_key] = gateway
        return gateway

    if exchange == ExchangeName.OKX:
        return OkxGateway()

    raise UnsupportedExchangeError(f"Unsupported exchange: {exchange}")
