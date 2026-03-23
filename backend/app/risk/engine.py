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
    account_available_balance: float | None = None,
    current_position_count: int | None = None,
    same_direction_position_count: int | None = None,
    max_single_trade_loss_pct: float | None = None,
    max_daily_exposure_pct: float | None = None,
    max_daily_loss_pct: float | None = None,
    max_positions: int | None = None,
    max_same_direction_positions: int | None = None,
    consecutive_losses: int = 0,
    consecutive_loss_pause_threshold: int | None = None,
    min_iv: float | None = None,
    max_iv: float | None = None,
    max_bid_ask_spread_ratio: float | None = None,
    min_activity: float | None = None,
    market_activity_score: float | None = None,
    overlap_ratio: float | None = None,
    max_overlap_ratio: float = 0.8,
    existing_short_symbols: list[str] | None = None,
) -> RiskCheckResult:
    single_loss_limit_pct = max_single_trade_loss_pct or settings.risk_max_single_trade_loss_pct
    daily_exposure_limit_pct = max_daily_exposure_pct or settings.risk_max_daily_exposure_pct
    daily_loss_limit_pct = max_daily_loss_pct or settings.risk_max_daily_loss_pct
    iv_limit = min_iv if min_iv is not None else settings.risk_min_iv
    iv_ceiling = max_iv if max_iv is not None else settings.iv_max
    spread_ratio_limit = (
        max_bid_ask_spread_ratio
        if max_bid_ask_spread_ratio is not None
        else settings.risk_max_bid_ask_spread_ratio
    )
    max_positions_limit = max_positions if max_positions is not None else settings.risk_max_positions
    max_same_direction_limit = (
        max_same_direction_positions
        if max_same_direction_positions is not None
        else settings.risk_max_same_direction_positions
    )
    consecutive_loss_limit = (
        consecutive_loss_pause_threshold
        if consecutive_loss_pause_threshold is not None
        else settings.risk_consecutive_loss_pause_threshold
    )
    min_activity_limit = min_activity if min_activity is not None else settings.liquidity_min_activity

    checks: dict[str, bool] = {}
    reasons: list[str] = []

    checks["strategy_score"] = candidate.score > 0
    if not checks["strategy_score"]:
        reasons.append("Strategy score is too low for auto execution.")

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
    if iv_ok and iv_ceiling is not None and candidate.iv_proxy is not None:
        iv_ok = candidate.iv_proxy <= iv_ceiling
        if not iv_ok:
            iv_reason = f"IV too high: {candidate.iv_proxy:.3f} > {iv_ceiling:.3f}"
    checks["iv_filter"] = iv_ok
    if not iv_ok:
        reasons.append(iv_reason)

    if market_activity_score is not None:
        activity_ok = market_activity_score >= min_activity_limit
        checks["market_activity"] = activity_ok
        if not activity_ok:
            reasons.append(
                f"Market activity {market_activity_score:.4f} below threshold {min_activity_limit:.4f}."
            )
    else:
        checks["market_activity"] = True

    if account_available_balance is not None:
        balance_ok = account_available_balance >= candidate.max_loss
        checks["available_balance"] = balance_ok
        if not balance_ok:
            reasons.append(
                f"Available balance {account_available_balance:.2f} is below max loss {candidate.max_loss:.2f}."
            )
    else:
        checks["available_balance"] = True

    if current_position_count is not None:
        count_ok = current_position_count < max_positions_limit
        checks["max_positions"] = count_ok
        if not count_ok:
            reasons.append(
                f"Open positions {current_position_count} reached limit {max_positions_limit}."
            )
    else:
        checks["max_positions"] = True

    if same_direction_position_count is not None:
        direction_ok = same_direction_position_count < max_same_direction_limit
        checks["same_direction_limit"] = direction_ok
        if not direction_ok:
            reasons.append(
                f"Same-direction positions {same_direction_position_count} reached limit {max_same_direction_limit}."
            )
    else:
        checks["same_direction_limit"] = True

    loss_pause_ok = consecutive_losses < consecutive_loss_limit
    checks["consecutive_loss_pause"] = loss_pause_ok
    if not loss_pause_ok:
        reasons.append(
            f"Consecutive losses {consecutive_losses} reached pause threshold {consecutive_loss_limit}."
        )

    existing_short_symbols = existing_short_symbols or []
    similar_exists = candidate.short_leg.quote.contract.symbol in set(existing_short_symbols)
    checks["position_similarity"] = not similar_exists
    if similar_exists:
        reasons.append("Similar short-leg position already exists; blocked to avoid risk stacking.")

    if overlap_ratio is not None:
        overlap_ok = overlap_ratio <= max_overlap_ratio
        checks["position_overlap"] = overlap_ok
        if not overlap_ok:
            reasons.append(
                f"Position overlap {overlap_ratio:.3f} exceeds limit {max_overlap_ratio:.3f}."
            )
    else:
        checks["position_overlap"] = True

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
            "max_positions_limit": float(max_positions_limit),
            "max_same_direction_limit": float(max_same_direction_limit),
            "consecutive_loss_pause_threshold": float(consecutive_loss_limit),
        },
    )
