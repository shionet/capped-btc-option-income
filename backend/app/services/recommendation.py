from __future__ import annotations

from datetime import date
from typing import Any

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
        strategy_overrides: dict[str, Any] | None = None,
        risk_overrides: dict[str, Any] | None = None,
    ) -> list[SpreadCandidate]:
        strategy_overrides = strategy_overrides or {}
        risk_overrides = risk_overrides or {}
        min_daily_return_on_risk = float(strategy_overrides.get("min_daily_return_on_risk", 0.0) or 0.0)
        min_annualized_return_on_risk = float(strategy_overrides.get("min_annualized_return_on_risk", 0.0) or 0.0)
        score_dte_weight = float(strategy_overrides.get("score_dte_weight", 1.0) or 0.0)
        quote = await self.market_data.get_btc_quote(exchange=exchange)
        chain = await self.market_data.get_option_chain(exchange=exchange, expiry=expiry)

        if strategy_type == StrategyType.BULL_PUT_SPREAD:
            candidates = generate_bull_put_spreads(
                spot_price=quote.price,
                option_chain=chain,
                settings=self.settings,
                sell_otm_min_pct=strategy_overrides.get("sell_otm_min_pct"),
                sell_otm_max_pct=strategy_overrides.get("sell_otm_max_pct"),
                buy_wing_min_pct=strategy_overrides.get("buy_wing_min_pct"),
                buy_wing_max_pct=strategy_overrides.get("buy_wing_max_pct"),
                min_net_premium=float(strategy_overrides.get("min_net_premium", 0.0)),
                min_reward_risk=float(strategy_overrides.get("min_reward_risk", 0.0)),
                max_width=strategy_overrides.get("max_width"),
            )
        elif strategy_type == StrategyType.BEAR_CALL_SPREAD:
            candidates = generate_bear_call_spreads(
                spot_price=quote.price,
                option_chain=chain,
                settings=self.settings,
                sell_otm_min_pct=strategy_overrides.get("sell_otm_min_pct"),
                sell_otm_max_pct=strategy_overrides.get("sell_otm_max_pct"),
                buy_wing_min_pct=strategy_overrides.get("buy_wing_min_pct"),
                buy_wing_max_pct=strategy_overrides.get("buy_wing_max_pct"),
                min_net_premium=float(strategy_overrides.get("min_net_premium", 0.0)),
                min_reward_risk=float(strategy_overrides.get("min_reward_risk", 0.0)),
                max_width=strategy_overrides.get("max_width"),
            )
        else:
            return []

        dte_min = strategy_overrides.get("allowed_dte_min")
        dte_max = strategy_overrides.get("allowed_dte_max")
        if dte_min is not None and dte_max is not None:
            preferred_pool = [c for c in candidates if int(dte_min) <= c.days_to_expiry <= int(dte_max)]
        else:
            allowed_dte = self.settings.allowed_dte_values()
            preferred_pool = [c for c in candidates if c.days_to_expiry in allowed_dte]
        primary_pool = preferred_pool if preferred_pool else candidates

        def _daily_return(candidate: SpreadCandidate) -> float:
            if candidate.daily_return_on_risk is not None:
                return candidate.daily_return_on_risk
            return candidate.reward_risk_ratio / max(candidate.days_to_expiry, 1)

        def _annualized_return(candidate: SpreadCandidate) -> float:
            if candidate.annualized_return_on_risk is not None:
                return candidate.annualized_return_on_risk
            return candidate.reward_risk_ratio * (365.0 / max(candidate.days_to_expiry, 1))

        def _effective_score(candidate: SpreadCandidate) -> float:
            # Keep original strategy score as base, then add time-normalized return preference.
            # The multiplier keeps daily-return contribution in a comparable score range.
            return candidate.score + score_dte_weight * (_daily_return(candidate) * 100.0)

        primary_pool.sort(key=_effective_score, reverse=True)
        if primary_pool is not candidates:
            candidates.sort(key=_effective_score, reverse=True)

        def _filter_with_risk(pool: list[SpreadCandidate]) -> list[SpreadCandidate]:
            out: list[SpreadCandidate] = []
            for item in pool:
                if _daily_return(item) < min_daily_return_on_risk:
                    continue
                if _annualized_return(item) < min_annualized_return_on_risk:
                    continue
                risk = run_risk_checks(
                    candidate=item,
                    account_equity=account_equity_for_filter,
                    daily_risk_exposure=0,
                    daily_realized_pnl=0,
                    settings=self.settings,
                    max_single_trade_loss_pct=risk_overrides.get("max_single_trade_loss_pct"),
                    max_daily_exposure_pct=risk_overrides.get("max_daily_exposure_pct"),
                    max_daily_loss_pct=risk_overrides.get("max_daily_loss_pct"),
                    max_positions=risk_overrides.get("max_positions"),
                    max_same_direction_positions=risk_overrides.get("max_same_direction_positions"),
                    consecutive_loss_pause_threshold=risk_overrides.get("consecutive_loss_pause_threshold"),
                    min_iv=risk_overrides.get("min_iv"),
                    max_iv=risk_overrides.get("max_iv"),
                    max_bid_ask_spread_ratio=risk_overrides.get("max_bid_ask_spread_ratio"),
                    min_activity=risk_overrides.get("min_activity"),
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
