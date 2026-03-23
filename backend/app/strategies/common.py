from __future__ import annotations

from datetime import date

from app.domain.enums import LegAction, OptionType, StrategyType
from app.domain.models import OptionLeg, OptionQuote, SpreadCandidate
from app.strategies.scorer import score_candidate


def build_vertical_candidate(
    *,
    strategy_type: StrategyType,
    spot_price: float,
    short_quote: OptionQuote,
    long_quote: OptionQuote,
) -> SpreadCandidate | None:
    if short_quote.contract.expiry != long_quote.contract.expiry:
        return None
    if short_quote.contract.option_type != long_quote.contract.option_type:
        return None
    if short_quote.contract.option_type == OptionType.PUT and short_quote.contract.strike <= long_quote.contract.strike:
        return None
    if short_quote.contract.option_type == OptionType.CALL and short_quote.contract.strike >= long_quote.contract.strike:
        return None

    net_credit = short_quote.bid - long_quote.ask
    if net_credit <= 0:
        return None

    width = abs(short_quote.contract.strike - long_quote.contract.strike)
    max_profit = net_credit
    max_loss = width - net_credit
    if max_loss <= 0:
        return None

    expiry = short_quote.contract.expiry
    dte = max((expiry - date.today()).days, 0)
    dte_nonzero = max(dte, 1)
    distance_pct = abs(short_quote.contract.strike - spot_price) / max(spot_price, 1e-9) * 100
    iv_values = [v for v in [short_quote.iv, long_quote.iv] if v is not None and v > 0]
    iv_proxy = sum(iv_values) / len(iv_values) if iv_values else None
    reward_risk_ratio = max_profit / max_loss
    candidate = SpreadCandidate(
        id=f"{strategy_type.value}:{short_quote.contract.symbol}:{long_quote.contract.symbol}",
        strategy_type=strategy_type,
        exchange=short_quote.contract.exchange,
        underlying=short_quote.contract.underlying,
        expiry=expiry,
        short_leg=OptionLeg(action=LegAction.SELL, quote=short_quote, quantity=1.0, price=short_quote.bid),
        long_leg=OptionLeg(action=LegAction.BUY, quote=long_quote, quantity=1.0, price=long_quote.ask),
        net_premium=net_credit,
        max_profit=max_profit,
        max_loss=max_loss,
        reward_risk_ratio=reward_risk_ratio,
        distance_to_spot_pct=distance_pct,
        days_to_expiry=dte,
        daily_return_on_risk=reward_risk_ratio / dte_nonzero,
        annualized_return_on_risk=reward_risk_ratio * (365.0 / dte_nonzero),
        iv_proxy=iv_proxy,
        reason_tags=[],
    )
    candidate.score = score_candidate(candidate)
    return candidate
