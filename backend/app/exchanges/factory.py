from app.core.config import Settings
from app.core.exceptions import UnsupportedExchangeError
from app.domain.enums import ExchangeName
from app.exchanges.base import ExchangeGateway
from app.exchanges.binance.client import BinanceRestClient
from app.exchanges.binance.gateway import BinanceGateway
from app.exchanges.okx.gateway import OkxGateway


def build_exchange_gateway(exchange: ExchangeName, settings: Settings) -> ExchangeGateway:
    if exchange == ExchangeName.BINANCE:
        client = BinanceRestClient(
            base_url=settings.binance_base_url,
            options_base_url=settings.binance_options_base_url,
            timeout_seconds=settings.binance_timeout_seconds,
            recv_window=settings.binance_recv_window,
            api_key=settings.binance_api_key,
            api_secret=settings.binance_api_secret,
        )
        return BinanceGateway(client)

    if exchange == ExchangeName.OKX:
        return OkxGateway()

    raise UnsupportedExchangeError(f"Unsupported exchange: {exchange}")
