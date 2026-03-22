from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_recommendation_service
from app.domain.enums import ExchangeName, StrategyType
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("/bull-put-spreads/recommendations")
async def get_bull_put_recommendations(
    exchange: ExchangeName = ExchangeName.BINANCE,
    expiry: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    account_equity: float = Query(default=100000, gt=0),
    service: RecommendationService = Depends(get_recommendation_service),
) -> dict:
    data = await service.recommend(
        strategy_type=StrategyType.BULL_PUT_SPREAD,
        exchange=exchange,
        expiry=expiry,
        limit=limit,
        account_equity_for_filter=account_equity,
    )
    return {"ok": True, "strategy_type": StrategyType.BULL_PUT_SPREAD.value, "count": len(data), "items": data}


@router.get("/bear-call-spreads/recommendations")
async def get_bear_call_recommendations(
    exchange: ExchangeName = ExchangeName.BINANCE,
    expiry: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    account_equity: float = Query(default=100000, gt=0),
    service: RecommendationService = Depends(get_recommendation_service),
) -> dict:
    data = await service.recommend(
        strategy_type=StrategyType.BEAR_CALL_SPREAD,
        exchange=exchange,
        expiry=expiry,
        limit=limit,
        account_equity_for_filter=account_equity,
    )
    return {"ok": True, "strategy_type": StrategyType.BEAR_CALL_SPREAD.value, "count": len(data), "items": data}
