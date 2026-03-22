from __future__ import annotations

from app.core.config import Settings
from app.domain.enums import OptionType, StrategyType
from app.domain.models import OptionQuote, SpreadCandidate
from app.strategies.common import build_vertical_candidate


def generate_bear_call_spreads(
    *,
    spot_price: float,
    option_chain: list[OptionQuote],
    settings: Settings,
) -> list[SpreadCandidate]:
    sell_min = settings.strategy_sell_otm_min_pct / 100.0
    sell_max = settings.strategy_sell_otm_max_pct / 100.0
    wing_min = settings.strategy_wing_width_min_pct / 100.0
    wing_max = settings.strategy_wing_width_max_pct / 100.0

    calls = [q for q in option_chain if q.contract.option_type == OptionType.CALL]
    candidates: list[SpreadCandidate] = []

    for short_quote in calls:
        short_distance = (short_quote.contract.strike - spot_price) / max(spot_price, 1e-9)
        if not (sell_min <= short_distance <= sell_max):
            continue

        for long_quote in calls:
            wing_distance = (long_quote.contract.strike - short_quote.contract.strike) / max(spot_price, 1e-9)
            if not (wing_min <= wing_distance <= wing_max):
                continue
            candidate = build_vertical_candidate(
                strategy_type=StrategyType.BEAR_CALL_SPREAD,
                spot_price=spot_price,
                short_quote=short_quote,
                long_quote=long_quote,
            )
            if candidate is None:
                continue
            candidates.append(candidate)

    candidates.sort(key=lambda x: x.score, reverse=True)
    return candidates
