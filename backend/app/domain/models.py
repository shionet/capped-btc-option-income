from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, computed_field

from app.domain.enums import ExchangeName, LegAction, OptionType, RunMode, StrategyType


class UnderlyingQuote(BaseModel):
    exchange: ExchangeName
    symbol: str
    price: float
    mark_price: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OptionContract(BaseModel):
    exchange: ExchangeName
    symbol: str
    underlying: str
    expiry: date
    strike: float
    option_type: OptionType
    contract_size: float = 1.0


class OptionQuote(BaseModel):
    contract: OptionContract
    bid: float
    ask: float
    mark: float | None = None
    iv: float | None = None
    bid_iv: float | None = None
    ask_iv: float | None = None
    delta: float | None = None
    theta: float | None = None
    gamma: float | None = None
    vega: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def bid_ask_spread_ratio(self) -> float:
        if self.ask <= 0:
            return 999.0
        return max(self.ask - self.bid, 0) / self.ask


class OptionLeg(BaseModel):
    action: LegAction
    quote: OptionQuote
    quantity: float = 1.0
    price: float


class SpreadCandidate(BaseModel):
    id: str
    strategy_type: StrategyType
    exchange: ExchangeName
    underlying: str
    expiry: date
    short_leg: OptionLeg
    long_leg: OptionLeg
    net_premium: float
    max_profit: float
    max_loss: float
    reward_risk_ratio: float
    distance_to_spot_pct: float
    days_to_expiry: int
    iv_proxy: float | None = None
    score: float = 0.0
    reason_tags: list[str] = Field(default_factory=list)


class StrategyRecommendation(BaseModel):
    candidate: SpreadCandidate
    score: float
    risk_flags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RiskCheckResult(BaseModel):
    allowed: bool
    reasons: list[str]
    checks: dict[str, bool] = Field(default_factory=dict)
    risk_metrics: dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PreviewOrder(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: float
    note: str


class ExecutionPreview(BaseModel):
    mode: RunMode
    strategy_type: StrategyType
    orders: list[PreviewOrder]
    estimated_fees: float
    max_risk: float
    risk_check: RiskCheckResult
    note: str


class PositionSnapshot(BaseModel):
    account_id: str | None = None
    open_positions: list[dict[str, Any]] = Field(default_factory=list)
    daily_realized_pnl: float = 0.0
    daily_unrealized_pnl: float = 0.0
    daily_risk_exposure: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BacktestReport(BaseModel):
    period: str
    total_return: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    monthly_returns: dict[str, float]
    assumptions: list[str] = Field(default_factory=list)
