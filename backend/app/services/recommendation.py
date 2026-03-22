from __future__ import annotations

from datetime import date

from app.core.config import Settings
from app.domain.enums import ExchangeName, StrategyType
from app.domain.models import SpreadCandidate
from app.risk.engine import run_risk_checks
from app.services.market_data import MarketDataService
from app.strategies.bear_call_spread import generate_bear_call_spreads
from app.strategies.bull_put_spread import generate_bull_put_spreads


class RecommendationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.market_data = MarketDataService(settings)

    async def recommend(
        self,
        *,
        strategy_type: StrategyType,
        exchange: ExchangeName,
        expiry: date | None,
        limit: int,
        account_equity_for_filter: float = 100000.0,
    ) -> list[SpreadCandidate]:
        quote = await self.market_data.get_btc_quote(exchange=exchange)
        chain = await self.market_data.get_option_chain(exchange=exchange, expiry=expiry)

        if strategy_type == StrategyType.BULL_PUT_SPREAD:
            candidates = generate_bull_put_spreads(
                spot_price=quote.price,
                option_chain=chain,
                settings=self.settings,
            )
        elif strategy_type == StrategyType.BEAR_CALL_SPREAD:
            candidates = generate_bear_call_spreads(
                spot_price=quote.price,
                option_chain=chain,
                settings=self.settings,
            )
        else:
            return []

        allowed_dte = self.settings.allowed_dte_values()
        preferred_pool = [c for c in candidates if c.days_to_expiry in allowed_dte]
        primary_pool = preferred_pool if preferred_pool else candidates

        def _filter_with_risk(pool: list[SpreadCandidate]) -> list[SpreadCandidate]:
            out: list[SpreadCandidate] = []
            for item in pool:
                risk = run_risk_checks(
                    candidate=item,
                    account_equity=account_equity_for_filter,
                    daily_risk_exposure=0,
                    daily_realized_pnl=0,
                    settings=self.settings,
                )
                if risk.allowed:
                    out.append(item)
                if len(out) >= limit:
                    break
            return out

        filtered = _filter_with_risk(primary_pool)
        # Fallback: if preferred DTE candidates exist but all blocked,
        # return broader expiries to avoid empty recommendation pages.
        if not filtered and preferred_pool and expiry is None:
            filtered = _filter_with_risk(candidates)
        return filtered
