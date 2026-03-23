from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.db.models import RiskBlockRecord
from app.domain.schemas import RiskCheckRequest, RiskCheckResponse
from app.risk.engine import run_risk_checks

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.post("/check", response_model=RiskCheckResponse)
async def risk_check(
    payload: RiskCheckRequest,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> RiskCheckResponse:
    result = run_risk_checks(
        candidate=payload.candidate,
        account_equity=payload.account_equity,
        account_available_balance=payload.account_available_balance,
        daily_risk_exposure=payload.daily_risk_exposure,
        daily_realized_pnl=payload.daily_realized_pnl,
        current_position_count=payload.current_position_count,
        same_direction_position_count=payload.same_direction_position_count,
        settings=settings,
        max_single_trade_loss_pct=payload.max_single_trade_loss_pct,
        max_daily_exposure_pct=payload.max_daily_exposure_pct,
        max_daily_loss_pct=payload.max_daily_loss_pct,
        max_positions=payload.max_positions,
        max_same_direction_positions=payload.max_same_direction_positions,
        consecutive_losses=payload.consecutive_losses,
        consecutive_loss_pause_threshold=payload.consecutive_loss_pause_threshold,
        min_iv=payload.min_iv,
        max_iv=payload.max_iv,
        max_bid_ask_spread_ratio=payload.max_bid_ask_spread_ratio,
        min_activity=payload.min_activity,
        market_activity_score=payload.market_activity_score,
        overlap_ratio=payload.overlap_ratio,
        max_overlap_ratio=payload.max_overlap_ratio,
        existing_short_symbols=payload.existing_short_symbols,
    )
    if not result.allowed:
        record = RiskBlockRecord(
            strategy_id=payload.candidate.id,
            reasons_json=json.dumps(result.reasons, ensure_ascii=True),
            checks_json=json.dumps(result.checks, ensure_ascii=True),
            metrics_json=json.dumps(result.risk_metrics, ensure_ascii=True),
        )
        db.add(record)
        db.commit()
    return RiskCheckResponse(ok=True, result=result)
