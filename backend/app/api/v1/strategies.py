from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_recommendation_service
from app.core.config import Settings, get_settings
from app.domain.enums import ExchangeName, StrategyType
from app.domain.models import SpreadCandidate
from app.exchanges.binance.client import BinanceRequestError
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


@router.get("/bull-put-spreads/recommendations")
async def get_bull_put_recommendations(
    exchange: ExchangeName = ExchangeName.BINANCE,
    expiry: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    account_equity: float = Query(default=100000, gt=0),
    service: RecommendationService = Depends(get_recommendation_service),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        data = await service.recommend(
            strategy_type=StrategyType.BULL_PUT_SPREAD,
            exchange=exchange,
            expiry=expiry,
            limit=limit,
            account_equity_for_filter=account_equity,
        )
    except BinanceRequestError as exc:
        status = 429 if exc.status_code == 429 else 503
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
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        data = await service.recommend(
            strategy_type=StrategyType.BEAR_CALL_SPREAD,
            exchange=exchange,
            expiry=expiry,
            limit=limit,
            account_equity_for_filter=account_equity,
        )
    except BinanceRequestError as exc:
        status = 429 if exc.status_code == 429 else 503
        raise HTTPException(
            status_code=status,
            detail={
                "message": "Market data provider is rate-limited or unavailable. Please retry shortly.",
                "provider_status_code": exc.status_code,
            },
        ) from exc
    items = [_with_position_sizing(item, account_equity, settings) for item in data]
    return {"ok": True, "strategy_type": StrategyType.BEAR_CALL_SPREAD.value, "count": len(items), "items": items}
