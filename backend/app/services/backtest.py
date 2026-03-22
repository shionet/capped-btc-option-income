from __future__ import annotations

from datetime import date

from app.domain.models import BacktestReport


class BacktestService:
    def run_mock(self, *, start: date | None, end: date | None, underlying: str) -> BacktestReport:
        period = f"{start or 'N/A'}~{end or 'N/A'}"
        return BacktestReport(
            period=period,
            total_return=0.084,
            max_drawdown=-0.051,
            win_rate=0.62,
            avg_win=91.2,
            avg_loss=-124.5,
            monthly_returns={
                "2026-01": 0.021,
                "2026-02": 0.033,
                "2026-03": 0.030,
            },
            assumptions=[
                "Mock report for MVP structure validation.",
                f"Underlying={underlying}",
                "No slippage model in mock stage.",
            ],
        )
