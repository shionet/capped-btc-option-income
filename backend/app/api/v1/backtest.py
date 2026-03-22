from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_backtest_service
from app.domain.schemas import BacktestRunRequest, BacktestRunResponse
from app.services.backtest import BacktestService

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run", response_model=BacktestRunResponse)
async def run_backtest(
    payload: BacktestRunRequest,
    service: BacktestService = Depends(get_backtest_service),
) -> BacktestRunResponse:
    report = service.run_mock(start=payload.start, end=payload.end, underlying=payload.underlying)
    return BacktestRunResponse(ok=True, report=report)
