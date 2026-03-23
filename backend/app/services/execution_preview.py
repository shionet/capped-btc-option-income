from __future__ import annotations

from app.core.config import Settings
from app.core.exceptions import LiveModeDisabledError
from app.domain.enums import RunMode
from app.domain.models import ExecutionPreview, PreviewOrder, SpreadCandidate
from app.risk.engine import run_risk_checks


class ExecutionPreviewService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def preview(
        self,
        *,
        mode: RunMode,
        quantity: float,
        candidate: SpreadCandidate,
        account_equity: float,
        daily_risk_exposure: float,
        daily_realized_pnl: float,
    ) -> ExecutionPreview:
        if mode == RunMode.LIVE_TRADING and not self.settings.live_trading_permitted():
            raise LiveModeDisabledError("Live mode is disabled by ENABLE_LIVE_TRADING=false.")

        risk = run_risk_checks(
            candidate=candidate,
            account_equity=account_equity,
            daily_risk_exposure=daily_risk_exposure,
            daily_realized_pnl=daily_realized_pnl,
            settings=self.settings,
        )
        orders = [
            PreviewOrder(
                symbol=candidate.long_leg.quote.contract.symbol,
                side="BUY",
                quantity=quantity,
                price=candidate.long_leg.price,
                note="Protective long leg must fill first.",
            ),
            PreviewOrder(
                symbol=candidate.short_leg.quote.contract.symbol,
                side="SELL",
                quantity=quantity,
                price=candidate.short_leg.price,
                note="Submit short leg only after protective leg is filled.",
            ),
        ]
        estimated_fees = sum(abs(o.price * o.quantity) for o in orders) * 0.0005
        return ExecutionPreview(
            mode=mode,
            strategy_type=candidate.strategy_type,
            orders=orders,
            estimated_fees=estimated_fees,
            max_risk=candidate.max_loss * quantity,
            risk_check=risk,
            note="Execution preview only. Real order placement requires explicit confirmation and mode controls.",
        )
