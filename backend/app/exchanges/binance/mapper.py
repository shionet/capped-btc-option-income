from __future__ import annotations

from datetime import date, datetime, timezone

from app.domain.enums import ExchangeName, OptionType
from app.domain.models import OptionContract, OptionQuote


def _to_float(value: str | float | int | None, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_expiry(ms: int | float | None) -> date:
    if not ms:
        return datetime.now(timezone.utc).date()
    return datetime.fromtimestamp(float(ms) / 1000, tz=timezone.utc).date()


def map_option_chain(
    *,
    exchange_info: dict,
    ticker_rows: list[dict],
    mark_rows: list[dict],
    underlying: str,
    expiry: date | None = None,
) -> list[OptionQuote]:
    symbol_to_symbol_info = {
        row["symbol"]: row
        for row in exchange_info.get("optionSymbols", [])
        if row.get("underlying") == underlying and row.get("status") == "TRADING"
    }
    ticker_map = {row.get("symbol"): row for row in ticker_rows}
    mark_map = {row.get("symbol"): row for row in mark_rows}

    quotes: list[OptionQuote] = []
    for symbol, symbol_info in symbol_to_symbol_info.items():
        contract_expiry = _to_expiry(symbol_info.get("expiryDate"))
        if expiry and contract_expiry != expiry:
            continue

        ticker = ticker_map.get(symbol, {})
        mark = mark_map.get(symbol, {})
        side = str(symbol_info.get("side", "")).upper()
        option_type = OptionType.CALL if side == "CALL" else OptionType.PUT

        contract = OptionContract(
            exchange=ExchangeName.BINANCE,
            symbol=symbol,
            underlying=underlying,
            expiry=contract_expiry,
            strike=_to_float(symbol_info.get("strikePrice")),
            option_type=option_type,
            contract_size=_to_float(symbol_info.get("unit"), 1.0),
        )
        bid = _to_float(ticker.get("bidPrice"))
        ask = _to_float(ticker.get("askPrice"))
        quote = OptionQuote(
            contract=contract,
            bid=bid,
            ask=ask,
            mark=_to_float(mark.get("markPrice"), _to_float(ticker.get("lastPrice"))),
            iv=_to_float(mark.get("markIV"), -1.0) if mark.get("markIV") is not None else None,
            bid_iv=_to_float(mark.get("bidIV"), -1.0) if mark.get("bidIV") is not None else None,
            ask_iv=_to_float(mark.get("askIV"), -1.0) if mark.get("askIV") is not None else None,
            delta=_to_float(mark.get("delta")) if mark.get("delta") is not None else None,
            theta=_to_float(mark.get("theta")) if mark.get("theta") is not None else None,
            gamma=_to_float(mark.get("gamma")) if mark.get("gamma") is not None else None,
            vega=_to_float(mark.get("vega")) if mark.get("vega") is not None else None,
            volume=_to_float(ticker.get("volume")) if ticker.get("volume") is not None else None,
            raw={"ticker": ticker, "mark": mark, "symbol_info": symbol_info},
        )
        # Binance may return -1 for unavailable IV; treat as unknown.
        if quote.iv is not None and quote.iv < 0:
            quote.iv = None
        if quote.bid_iv is not None and quote.bid_iv < 0:
            quote.bid_iv = None
        if quote.ask_iv is not None and quote.ask_iv < 0:
            quote.ask_iv = None
        quotes.append(quote)

    return quotes
