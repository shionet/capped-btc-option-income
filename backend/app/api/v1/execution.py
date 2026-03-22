from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_execution_preview_service
from app.core.exceptions import LiveModeDisabledError
from app.domain.schemas import ExecutionPreviewRequest, ExecutionPreviewResponse
from app.services.execution_preview import ExecutionPreviewService

router = APIRouter(prefix="/api/execution", tags=["execution"])


@router.post("/preview", response_model=ExecutionPreviewResponse)
async def execution_preview(
    payload: ExecutionPreviewRequest,
    service: ExecutionPreviewService = Depends(get_execution_preview_service),
) -> ExecutionPreviewResponse:
    try:
        preview = service.preview(
            mode=payload.mode,
            quantity=payload.quantity,
            candidate=payload.candidate,
            account_equity=payload.account_equity,
            daily_risk_exposure=payload.daily_risk_exposure,
            daily_realized_pnl=payload.daily_realized_pnl,
        )
    except LiveModeDisabledError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ExecutionPreviewResponse(ok=True, preview=preview)
