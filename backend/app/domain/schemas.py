from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums import ExchangeName, RunMode, StrategyType
from app.domain.models import BacktestReport, ExecutionPreview, RiskCheckResult, SpreadCandidate


class OptionsChainQuery(BaseModel):
    exchange: ExchangeName = ExchangeName.BINANCE
    expiry: date | None = None
    limit: int = Field(default=300, ge=1, le=2000)


class RecommendationQuery(BaseModel):
    exchange: ExchangeName = ExchangeName.BINANCE
    expiry: date | None = None
    limit: int = Field(default=20, ge=1, le=200)


class RiskCheckRequest(BaseModel):
    account_equity: float = Field(gt=0)
    candidate: SpreadCandidate
    daily_risk_exposure: float = 0.0
    daily_realized_pnl: float = 0.0
    max_single_trade_loss_pct: float | None = None
    max_daily_exposure_pct: float | None = None
    max_daily_loss_pct: float | None = None
    min_iv: float | None = None
    max_bid_ask_spread_ratio: float | None = None
    existing_short_symbols: list[str] = Field(default_factory=list)


class ExecutionPreviewRequest(BaseModel):
    mode: RunMode = RunMode.DRY_RUN
    quantity: float = Field(default=1.0, gt=0)
    candidate: SpreadCandidate
    account_equity: float = Field(default=10000, gt=0)
    daily_risk_exposure: float = 0.0
    daily_realized_pnl: float = 0.0


class BacktestRunRequest(BaseModel):
    strategy_type: StrategyType = StrategyType.BULL_PUT_SPREAD
    start: date | None = None
    end: date | None = None
    underlying: str = "BTCUSDT"


class BacktestRunResponse(BaseModel):
    ok: bool = True
    report: BacktestReport


class RiskCheckResponse(BaseModel):
    ok: bool = True
    result: RiskCheckResult


class ExecutionPreviewResponse(BaseModel):
    ok: bool = True
    preview: ExecutionPreview
