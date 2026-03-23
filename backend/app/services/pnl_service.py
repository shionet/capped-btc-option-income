from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import PnlDailyRecord, PositionRecord


def _f(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


class PnlService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self) -> dict[str, Any]:
        rows = self.db.query(PositionRecord).all()
        open_rows = [row for row in rows if row.status in {"opening", "open", "closing"}]
        closed_rows = [row for row in rows if row.status == "closed"]
        today = date.today().isoformat()

        unrealized = sum(_f(row.unrealized_pnl) for row in open_rows)
        realized = sum(_f(row.realized_pnl) for row in closed_rows)
        daily_rows = self.db.query(PnlDailyRecord).order_by(desc(PnlDailyRecord.date)).limit(30).all()
        today_row = next((row for row in daily_rows if row.date.isoformat() == today), None)
        daily_pnl = _f(today_row.total_pnl) if today_row else 0.0
        weekly_pnl = sum(_f(row.total_pnl) for row in daily_rows[:7])
        monthly_pnl = sum(_f(row.total_pnl) for row in daily_rows)

        return {
            "realized_pnl": realized,
            "unrealized_pnl": unrealized,
            "today_pnl": daily_pnl,
            "week_pnl": weekly_pnl,
            "month_pnl": monthly_pnl,
            "open_positions": len(open_rows),
            "closed_positions": len(closed_rows),
        }

    def history(self, limit: int = 120) -> list[dict[str, Any]]:
        rows = self.db.query(PnlDailyRecord).order_by(desc(PnlDailyRecord.date)).limit(limit).all()
        return [
            {
                "date": row.date.isoformat(),
                "realized_pnl": _f(row.realized_pnl),
                "unrealized_pnl": _f(row.unrealized_pnl),
                "total_pnl": _f(row.total_pnl),
                "equity": _f(row.equity),
                "drawdown": _f(row.drawdown),
                "win_rate": _f(row.win_rate),
            }
            for row in rows
        ]

    def by_strategy(self) -> list[dict[str, Any]]:
        rows = self.db.query(PositionRecord).all()
        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            key = row.strategy_type
            grouped.setdefault(
                key,
                {
                    "strategy_type": key,
                    "realized_pnl": 0.0,
                    "unrealized_pnl": 0.0,
                    "count": 0,
                    "wins": 0,
                },
            )
            grouped[key]["count"] += 1
            grouped[key]["realized_pnl"] += _f(row.realized_pnl)
            grouped[key]["unrealized_pnl"] += _f(row.unrealized_pnl)
            if _f(row.realized_pnl) > 0:
                grouped[key]["wins"] += 1

        out: list[dict[str, Any]] = []
        for value in grouped.values():
            count = max(value["count"], 1)
            value["win_rate"] = value["wins"] / count
            out.append(value)
        return out
