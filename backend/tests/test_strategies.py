from datetime import date, timedelta

from app.core.config import Settings
from app.domain.enums import ExchangeName, OptionType
from app.domain.models import OptionContract, OptionQuote
from app.strategies.bear_call_spread import generate_bear_call_spreads
from app.strategies.bull_put_spread import generate_bull_put_spreads


def _quote(symbol: str, strike: float, option_type: OptionType, bid: float, ask: float) -> OptionQuote:
    return OptionQuote(
        contract=OptionContract(
            exchange=ExchangeName.BINANCE,
            symbol=symbol,
            underlying="BTCUSDT",
            expiry=date.today() + timedelta(days=1),
            strike=strike,
            option_type=option_type,
            contract_size=1.0,
        ),
        bid=bid,
        ask=ask,
        mark=(bid + ask) / 2,
        iv=0.7,
    )


def test_generate_bull_put_spreads_returns_credit_candidates() -> None:
    settings = Settings()
    chain = [
        _quote("P1", 98000, OptionType.PUT, bid=120, ask=130),
        _quote("P2", 95000, OptionType.PUT, bid=80, ask=90),
        _quote("P3", 92000, OptionType.PUT, bid=30, ask=35),
    ]
    data = generate_bull_put_spreads(spot_price=100000, option_chain=chain, settings=settings)
    assert data
    assert data[0].net_premium > 0
    assert data[0].max_loss > 0


def test_generate_bear_call_spreads_returns_credit_candidates() -> None:
    settings = Settings()
    chain = [
        _quote("C1", 102000, OptionType.CALL, bid=120, ask=130),
        _quote("C2", 106000, OptionType.CALL, bid=70, ask=80),
        _quote("C3", 110000, OptionType.CALL, bid=20, ask=25),
    ]
    data = generate_bear_call_spreads(spot_price=100000, option_chain=chain, settings=settings)
    assert data
    assert data[0].net_premium > 0
    assert data[0].max_loss > 0
