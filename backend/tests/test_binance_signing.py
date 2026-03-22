import hashlib
import hmac
from urllib.parse import urlencode

from app.exchanges.binance.client import BinanceRestClient


def test_build_signed_params_generates_expected_signature(monkeypatch) -> None:
    monkeypatch.setattr("app.exchanges.binance.client.time.time", lambda: 1700000000.123)

    client = BinanceRestClient(
        base_url="https://api.binance.com",
        options_base_url="https://eapi.binance.com",
        api_key="k",
        api_secret="test-secret",
        recv_window=5000,
    )

    params = client._build_signed_params({"symbol": "BTCUSDT"})
    expected_payload = {
        "symbol": "BTCUSDT",
        "timestamp": 1700000000123,
        "recvWindow": 5000,
    }
    expected_signature = hmac.new(
        b"test-secret",
        urlencode(expected_payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    assert params["symbol"] == "BTCUSDT"
    assert params["timestamp"] == 1700000000123
    assert params["recvWindow"] == 5000
    assert params["signature"] == expected_signature
