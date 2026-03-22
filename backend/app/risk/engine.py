from __future__ import annotations

from app.core.config import Settings
from app.domain.models import RiskCheckResult, SpreadCandidate
from app.risk.iv_filter import check_iv_threshold
from app.risk.liquidity import check_liquidity


def run_risk_checks(
    *,
    candidate: SpreadCandidate,
    account_equity: float,
    daily_risk_exposure: float,
    daily_realized_pnl: float,
    settings: Settings,
    max_single_trade_loss_pct: float | None = None,
    max_daily_exposure_pct: float | None = None,
    max_daily_loss_pct: float | None = None,
    min_iv: float | None = None,
    max_bid_ask_spread_ratio: float | None = None,
    existing_short_symbols: list[str] | None = None,
) -> RiskCheckResult:
    single_loss_limit_pct = max_single_trade_loss_pct or settings.risk_max_single_trade_loss_pct
    daily_exposure_limit_pct = max_daily_exposure_pct or settings.risk_max_daily_exposure_pct
    daily_loss_limit_pct = max_daily_loss_pct or settings.risk_max_daily_loss_pct
    iv_limit = min_iv if min_iv is not None else settings.risk_min_iv
    spread_ratio_limit = (
        max_bid_ask_spread_ratio
        if max_bid_ask_spread_ratio is not None
        else settings.risk_max_bid_ask_spread_ratio
    )

    checks: dict[str, bool] = {}
    reasons: list[str] = []

    max_single_loss_allowed = account_equity * single_loss_limit_pct
    check_single = candidate.max_loss <= max_single_loss_allowed
    checks["single_trade_loss"] = check_single
    if not check_single:
        reasons.append(
            f"Max loss {candidate.max_loss:.2f} exceeds single-trade cap {max_single_loss_allowed:.2f}."
        )

    daily_exposure_allowed = account_equity * daily_exposure_limit_pct
    projected_daily_exposure = daily_risk_exposure + candidate.max_loss
    check_exposure = projected_daily_exposure <= daily_exposure_allowed
    checks["daily_exposure"] = check_exposure
    if not check_exposure:
        reasons.append(
            f"Projected daily exposure {projected_daily_exposure:.2f} exceeds cap {daily_exposure_allowed:.2f}."
        )

    daily_loss_allowed = account_equity * daily_loss_limit_pct
    check_daily_loss = abs(min(daily_realized_pnl, 0.0)) <= daily_loss_allowed
    checks["daily_loss_guard"] = check_daily_loss
    if not check_daily_loss:
        reasons.append(
            f"Daily realized loss {abs(min(daily_realized_pnl, 0.0)):.2f} exceeds loss guard {daily_loss_allowed:.2f}."
        )

    liquidity_ok, liquidity_reason = check_liquidity(
        candidate,
        max_bid_ask_spread_ratio=spread_ratio_limit,
        min_bid_price=settings.risk_min_bid_price,
    )
    checks["liquidity"] = liquidity_ok
    if not liquidity_ok:
        reasons.append(liquidity_reason)

    iv_ok, iv_reason = check_iv_threshold(candidate, iv_limit)
    checks["iv_filter"] = iv_ok
    if not iv_ok:
        reasons.append(iv_reason)

    existing_short_symbols = existing_short_symbols or []
    similar_exists = candidate.short_leg.quote.contract.symbol in set(existing_short_symbols)
    checks["position_similarity"] = not similar_exists
    if similar_exists:
        reasons.append("Similar short-leg position already exists; blocked to avoid risk stacking.")

    allowed = all(checks.values())
    if allowed:
        reasons.append("All risk checks passed.")

    return RiskCheckResult(
        allowed=allowed,
        reasons=reasons,
        checks=checks,
        risk_metrics={
            "account_equity": account_equity,
            "candidate_max_loss": candidate.max_loss,
            "single_trade_loss_limit": max_single_loss_allowed,
            "daily_exposure_limit": daily_exposure_allowed,
            "projected_daily_exposure": projected_daily_exposure,
            "daily_loss_limit": daily_loss_allowed,
        },
    )
