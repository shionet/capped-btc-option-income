from datetime import date, timedelta

from app.core.config import Settings
from app.domain.enums import ExchangeName, LegAction, OptionType, StrategyType
from app.domain.models import OptionContract, OptionLeg, OptionQuote, SpreadCandidate
from app.risk.engine import run_risk_checks


def _candidate() -> SpreadCandidate:
    expiry = date.today() + timedelta(days=1)
    short_quote = OptionQuote(
        contract=OptionContract(
            exchange=ExchangeName.BINANCE,
            symbol="BTC-TEST-SHORT-P",
            underlying="BTCUSDT",
            expiry=expiry,
            strike=98000,
            option_type=OptionType.PUT,
            contract_size=1.0,
        ),
        bid=130,
        ask=140,
        mark=135,
        iv=0.8,
    )
    long_quote = OptionQuote(
        contract=OptionContract(
            exchange=ExchangeName.BINANCE,
            symbol="BTC-TEST-LONG-P",
            underlying="BTCUSDT",
            expiry=expiry,
            strike=95000,
            option_type=OptionType.PUT,
            contract_size=1.0,
        ),
        bid=70,
        ask=80,
        mark=75,
        iv=0.78,
    )
    return SpreadCandidate(
        id="x",
        strategy_type=StrategyType.BULL_PUT_SPREAD,
        exchange=ExchangeName.BINANCE,
        underlying="BTCUSDT",
        expiry=expiry,
        short_leg=OptionLeg(action=LegAction.SELL, quote=short_quote, quantity=1, price=130),
        long_leg=OptionLeg(action=LegAction.BUY, quote=long_quote, quantity=1, price=80),
        net_premium=50,
        max_profit=50,
        max_loss=2950,
        reward_risk_ratio=50 / 2950,
        distance_to_spot_pct=2.0,
        days_to_expiry=1,
        iv_proxy=0.79,
    )


def test_risk_engine_blocks_when_single_loss_too_high() -> None:
    settings = Settings(risk_max_single_trade_loss_pct=0.01)
    result = run_risk_checks(
        candidate=_candidate(),
        account_equity=10000,
        daily_risk_exposure=0,
        daily_realized_pnl=0,
        settings=settings,
    )
    assert not result.allowed
    assert result.checks["single_trade_loss"] is False


def test_risk_engine_blocks_similar_position() -> None:
    settings = Settings(risk_max_single_trade_loss_pct=1.0)
    c = _candidate()
    result = run_risk_checks(
        candidate=c,
        account_equity=10000,
        daily_risk_exposure=0,
        daily_realized_pnl=0,
        settings=settings,
        existing_short_symbols=[c.short_leg.quote.contract.symbol],
    )
    assert not result.allowed
    assert result.checks["position_similarity"] is False
