from app.exchanges.binance.mapper import map_option_chain


def test_map_option_chain_normalizes_fields() -> None:
    exchange_info = {
        "optionSymbols": [
            {
                "expiryDate": 1774598400000,
                "symbol": "BTC-260327-100000-C",
                "side": "CALL",
                "strikePrice": "100000.000",
                "underlying": "BTCUSDT",
                "unit": 1,
                "status": "TRADING",
            }
        ]
    }
    ticker_rows = [{"symbol": "BTC-260327-100000-C", "bidPrice": "4", "askPrice": "5", "volume": "1.2"}]
    mark_rows = [{"symbol": "BTC-260327-100000-C", "markPrice": "4.5", "markIV": "0.88"}]

    data = map_option_chain(
        exchange_info=exchange_info,
        ticker_rows=ticker_rows,
        mark_rows=mark_rows,
        underlying="BTCUSDT",
    )
    assert len(data) == 1
    item = data[0]
    assert item.contract.symbol == "BTC-260327-100000-C"
    assert item.bid == 4
    assert item.ask == 5
    assert item.iv == 0.88
