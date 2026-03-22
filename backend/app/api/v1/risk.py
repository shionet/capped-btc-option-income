from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.domain.schemas import RiskCheckRequest, RiskCheckResponse
from app.risk.engine import run_risk_checks

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.post("/check", response_model=RiskCheckResponse)
async def risk_check(payload: RiskCheckRequest, settings: Settings = Depends(get_settings)) -> RiskCheckResponse:
    result = run_risk_checks(
        candidate=payload.candidate,
        account_equity=payload.account_equity,
        daily_risk_exposure=payload.daily_risk_exposure,
        daily_realized_pnl=payload.daily_realized_pnl,
        settings=settings,
        max_single_trade_loss_pct=payload.max_single_trade_loss_pct,
        max_daily_exposure_pct=payload.max_daily_exposure_pct,
        max_daily_loss_pct=payload.max_daily_loss_pct,
        min_iv=payload.min_iv,
        max_bid_ask_spread_ratio=payload.max_bid_ask_spread_ratio,
        existing_short_symbols=payload.existing_short_symbols,
    )
    return RiskCheckResponse(ok=True, result=result)
