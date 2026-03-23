from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_config_service, get_recommendation_service
from app.core.config import Settings, get_settings
from app.domain.enums import ConfigDomain
from app.domain.enums import ExchangeName, StrategyType
from app.domain.models import SpreadCandidate
from app.exchanges.binance.client import BinanceRequestError
from app.services.config_service import ConfigService
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


def _with_position_sizing(candidate: SpreadCandidate, account_equity: float, settings: Settings) -> dict:
    max_trade_risk = account_equity * settings.risk_max_single_trade_loss_pct
    per_spread_loss = max(candidate.max_loss, 1e-9)
    max_position_size = int(max_trade_risk // per_spread_loss)
    payload = candidate.model_dump(mode="json")
    payload["max_trade_risk"] = max_trade_risk
    payload["max_position_size"] = max_position_size
    payload["position_size_allowed"] = max_position_size >= 1
    return payload


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


@router.get("/bull-put-spreads/recommendations")
async def get_bull_put_recommendations(
    exchange: ExchangeName = ExchangeName.BINANCE,
    expiry: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    account_equity: float = Query(default=100000, gt=0),
    service: RecommendationService = Depends(get_recommendation_service),
    config_service: ConfigService = Depends(get_config_service),
    settings: Settings = Depends(get_settings),
) -> dict:
    strategy_cfg = config_service.get_config(ConfigDomain.STRATEGY)["payload"]
    risk_cfg = config_service.get_config(ConfigDomain.RISK)["payload"]

    base_cfg = strategy_cfg.get("base", {})
    bps_cfg = strategy_cfg.get("bull_put_spread", {})
    iv_cfg = strategy_cfg.get("iv", {})
    liquidity_cfg = strategy_cfg.get("liquidity", {})
    configured_limit = max(_to_int(base_cfg.get("candidate_limit"), default=limit), 1)
    effective_limit = min(limit, configured_limit)

    strategy_overrides = {
        "allowed_dte_min": _to_int(base_cfg.get("allowed_dte_min"), 0),
        "allowed_dte_max": _to_int(base_cfg.get("allowed_dte_max"), 365),
        "min_daily_return_on_risk": _to_float(base_cfg.get("min_daily_return_on_risk"), 0.0),
        "min_annualized_return_on_risk": _to_float(base_cfg.get("min_annualized_return_on_risk"), 0.0),
        "score_dte_weight": _to_float(base_cfg.get("score_dte_weight"), 1.0),
        "sell_otm_min_pct": _to_float(bps_cfg.get("sell_otm_min_pct"), settings.strategy_bull_put_sell_otm_min_pct),
        "sell_otm_max_pct": _to_float(bps_cfg.get("sell_otm_max_pct"), settings.strategy_bull_put_sell_otm_max_pct),
        "buy_wing_min_pct": _to_float(bps_cfg.get("buy_wing_min_pct"), settings.strategy_bull_put_buy_wing_min_pct),
        "buy_wing_max_pct": _to_float(bps_cfg.get("buy_wing_max_pct"), settings.strategy_bull_put_buy_wing_max_pct),
        "min_net_premium": _to_float(bps_cfg.get("min_net_premium"), settings.strategy_bull_put_min_net_premium),
        "min_reward_risk": _to_float(bps_cfg.get("min_reward_risk"), settings.strategy_bull_put_min_reward_risk),
        "max_width": _to_float(bps_cfg.get("max_width"), settings.strategy_bull_put_max_width),
    }
    risk_overrides = {
        "max_single_trade_loss_pct": _to_float(
            risk_cfg.get("max_single_trade_loss_pct"), settings.risk_max_single_trade_loss_pct
        ),
        "max_daily_exposure_pct": _to_float(
            risk_cfg.get("max_daily_exposure_pct"), settings.risk_max_daily_exposure_pct
        ),
        "max_daily_loss_pct": _to_float(risk_cfg.get("max_daily_loss_pct"), settings.risk_max_daily_loss_pct),
        "max_positions": _to_int(risk_cfg.get("max_positions"), settings.risk_max_positions),
        "max_same_direction_positions": _to_int(
            risk_cfg.get("max_same_direction_positions"), settings.risk_max_same_direction_positions
        ),
        "consecutive_loss_pause_threshold": _to_int(
            risk_cfg.get("consecutive_loss_pause_threshold"), settings.risk_consecutive_loss_pause_threshold
        ),
        "min_iv": _to_float(iv_cfg.get("min_iv"), settings.iv_min) if iv_cfg.get("enabled", True) else None,
        "max_iv": iv_cfg.get("max_iv") if iv_cfg.get("enabled", True) else None,
        "max_bid_ask_spread_ratio": _to_float(
            liquidity_cfg.get("max_bid_ask_spread"), settings.liquidity_max_bid_ask_spread
        ),
        "min_activity": _to_float(liquidity_cfg.get("min_activity"), settings.liquidity_min_activity),
    }

    try:
        data = await service.recommend(
            strategy_type=StrategyType.BULL_PUT_SPREAD,
            exchange=exchange,
            expiry=expiry,
            limit=effective_limit,
            account_equity_for_filter=account_equity,
            strategy_overrides=strategy_overrides,
            risk_overrides=risk_overrides,
        )
    except BinanceRequestError as exc:
        status = 429 if exc.status_code in {418, 429} else 503
        raise HTTPException(
            status_code=status,
            detail={
                "message": "Market data provider is rate-limited or unavailable. Please retry shortly.",
                "provider_status_code": exc.status_code,
            },
        ) from exc
    items = [_with_position_sizing(item, account_equity, settings) for item in data]
    return {"ok": True, "strategy_type": StrategyType.BULL_PUT_SPREAD.value, "count": len(items), "items": items}


@router.get("/bear-call-spreads/recommendations")
async def get_bear_call_recommendations(
    exchange: ExchangeName = ExchangeName.BINANCE,
    expiry: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    account_equity: float = Query(default=100000, gt=0),
    service: RecommendationService = Depends(get_recommendation_service),
    config_service: ConfigService = Depends(get_config_service),
    settings: Settings = Depends(get_settings),
) -> dict:
    strategy_cfg = config_service.get_config(ConfigDomain.STRATEGY)["payload"]
    risk_cfg = config_service.get_config(ConfigDomain.RISK)["payload"]

    base_cfg = strategy_cfg.get("base", {})
    bcs_cfg = strategy_cfg.get("bear_call_spread", {})
    iv_cfg = strategy_cfg.get("iv", {})
    liquidity_cfg = strategy_cfg.get("liquidity", {})
    configured_limit = max(_to_int(base_cfg.get("candidate_limit"), default=limit), 1)
    effective_limit = min(limit, configured_limit)

    strategy_overrides = {
        "allowed_dte_min": _to_int(base_cfg.get("allowed_dte_min"), 0),
        "allowed_dte_max": _to_int(base_cfg.get("allowed_dte_max"), 365),
        "min_daily_return_on_risk": _to_float(base_cfg.get("min_daily_return_on_risk"), 0.0),
        "min_annualized_return_on_risk": _to_float(base_cfg.get("min_annualized_return_on_risk"), 0.0),
        "score_dte_weight": _to_float(base_cfg.get("score_dte_weight"), 1.0),
        "sell_otm_min_pct": _to_float(bcs_cfg.get("sell_otm_min_pct"), settings.strategy_bear_call_sell_otm_min_pct),
        "sell_otm_max_pct": _to_float(bcs_cfg.get("sell_otm_max_pct"), settings.strategy_bear_call_sell_otm_max_pct),
        "buy_wing_min_pct": _to_float(bcs_cfg.get("buy_wing_min_pct"), settings.strategy_bear_call_buy_wing_min_pct),
        "buy_wing_max_pct": _to_float(bcs_cfg.get("buy_wing_max_pct"), settings.strategy_bear_call_buy_wing_max_pct),
        "min_net_premium": _to_float(bcs_cfg.get("min_net_premium"), settings.strategy_bear_call_min_net_premium),
        "min_reward_risk": _to_float(bcs_cfg.get("min_reward_risk"), settings.strategy_bear_call_min_reward_risk),
        "max_width": _to_float(bcs_cfg.get("max_width"), settings.strategy_bear_call_max_width),
    }
    risk_overrides = {
        "max_single_trade_loss_pct": _to_float(
            risk_cfg.get("max_single_trade_loss_pct"), settings.risk_max_single_trade_loss_pct
        ),
        "max_daily_exposure_pct": _to_float(
            risk_cfg.get("max_daily_exposure_pct"), settings.risk_max_daily_exposure_pct
        ),
        "max_daily_loss_pct": _to_float(risk_cfg.get("max_daily_loss_pct"), settings.risk_max_daily_loss_pct),
        "max_positions": _to_int(risk_cfg.get("max_positions"), settings.risk_max_positions),
        "max_same_direction_positions": _to_int(
            risk_cfg.get("max_same_direction_positions"), settings.risk_max_same_direction_positions
        ),
        "consecutive_loss_pause_threshold": _to_int(
            risk_cfg.get("consecutive_loss_pause_threshold"), settings.risk_consecutive_loss_pause_threshold
        ),
        "min_iv": _to_float(iv_cfg.get("min_iv"), settings.iv_min) if iv_cfg.get("enabled", True) else None,
        "max_iv": iv_cfg.get("max_iv") if iv_cfg.get("enabled", True) else None,
        "max_bid_ask_spread_ratio": _to_float(
            liquidity_cfg.get("max_bid_ask_spread"), settings.liquidity_max_bid_ask_spread
        ),
        "min_activity": _to_float(liquidity_cfg.get("min_activity"), settings.liquidity_min_activity),
    }

    try:
        data = await service.recommend(
            strategy_type=StrategyType.BEAR_CALL_SPREAD,
            exchange=exchange,
            expiry=expiry,
            limit=effective_limit,
            account_equity_for_filter=account_equity,
            strategy_overrides=strategy_overrides,
            risk_overrides=risk_overrides,
        )
    except BinanceRequestError as exc:
        status = 429 if exc.status_code in {418, 429} else 503
        raise HTTPException(
            status_code=status,
            detail={
                "message": "Market data provider is rate-limited or unavailable. Please retry shortly.",
                "provider_status_code": exc.status_code,
            },
        ) from exc
    items = [_with_position_sizing(item, account_equity, settings) for item in data]
    return {"ok": True, "strategy_type": StrategyType.BEAR_CALL_SPREAD.value, "count": len(items), "items": items}
