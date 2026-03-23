from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import PositionLegRecord, PositionRecord


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


class PositionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _serialize_position(self, row: PositionRecord) -> dict[str, Any]:
        legs = self.db.query(PositionLegRecord).filter(
            PositionLegRecord.position_uid == row.position_uid
        ).order_by(PositionLegRecord.id.asc()).all()
        return {
            "position_id": row.position_uid,
            "strategy_type": row.strategy_type,
            "underlying": row.underlying,
            "exchange": row.exchange,
            "opened_at": row.opened_at.isoformat() if row.opened_at else None,
            "closed_at": row.closed_at.isoformat() if row.closed_at else None,
            "expiry": row.expiry.isoformat() if row.expiry else None,
            "quantity": row.quantity,
            "net_credit_open": _to_float(row.net_credit_open),
            "current_value": _to_float(row.current_value),
            "unrealized_pnl": _to_float(row.unrealized_pnl),
            "realized_pnl": _to_float(row.realized_pnl),
            "max_profit": _to_float(row.max_profit),
            "max_loss": _to_float(row.max_loss),
            "risk_utilization": _to_float(row.risk_utilization),
            "margin_used": _to_float(row.margin_used),
            "status": row.status,
            "legs": [
                {
                    "role": leg.leg_role,
                    "side": leg.side,
                    "symbol": leg.symbol,
                    "strike": _to_float(leg.strike),
                    "option_type": leg.option_type,
                    "expiry": leg.expiry.isoformat() if leg.expiry else None,
                    "quantity": leg.quantity,
                    "avg_open_price": _to_float(leg.avg_open_price),
                    "avg_close_price": _to_float(leg.avg_close_price),
                    "state": leg.state,
                }
                for leg in legs
            ],
        }

    def list_positions(self, *, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        query = self.db.query(PositionRecord)
        if status:
            query = query.filter(PositionRecord.status == status)
        rows = query.order_by(desc(PositionRecord.id)).limit(limit).all()
        return [self._serialize_position(row) for row in rows]

    def get_position(self, position_id: str) -> dict[str, Any] | None:
        row = self.db.query(PositionRecord).filter(PositionRecord.position_uid == position_id).first()
        if not row:
            return None
        return self._serialize_position(row)

    def close_position(self, position_id: str, actor: str = "user") -> dict[str, Any] | None:
        row = self.db.query(PositionRecord).filter(PositionRecord.position_uid == position_id).first()
        if not row:
            return None
        row.status = "closed"
        row.closed_at = datetime.now(timezone.utc)
        row.notes = f"Closed by {actor}"
        self.db.commit()
        self.db.refresh(row)
        return self._serialize_position(row)

    def create_mock_position(self, *, strategy_type: str = "bull_put_spread") -> dict[str, Any]:
        uid = f"pos_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        row = PositionRecord(
            position_uid=uid,
            strategy_type=strategy_type,
            underlying="BTC",
            exchange="binance",
            quantity=1,
            net_credit_open=120.0,
            current_value=90.0,
            realized_pnl=0.0,
            unrealized_pnl=30.0,
            max_profit=120.0,
            max_loss=1880.0,
            risk_utilization=0.12,
            margin_used=700.0,
            status="open",
            opened_at=now,
        )
        self.db.add(row)
        self.db.flush()

        short_leg = PositionLegRecord(
            position_uid=uid,
            leg_role="short",
            side="SELL",
            symbol="BTC-TEST-SHORT",
            strike=95000.0,
            option_type="put",
            expiry=now.date(),
            quantity=1,
            avg_open_price=120.0,
            state="open",
        )
        long_leg = PositionLegRecord(
            position_uid=uid,
            leg_role="long",
            side="BUY",
            symbol="BTC-TEST-LONG",
            strike=92000.0,
            option_type="put",
            expiry=now.date(),
            quantity=1,
            avg_open_price=40.0,
            state="open",
        )
        self.db.add(short_leg)
        self.db.add(long_leg)
        self.db.commit()
        self.db.refresh(row)
        return self._serialize_position(row)

    def portfolio_summary(self) -> dict[str, Any]:
        rows = self.db.query(PositionRecord).order_by(desc(PositionRecord.id)).all()
        open_rows = [row for row in rows if row.status in {"opening", "open", "closing"}]
        grouped_by_strategy: dict[str, dict[str, Any]] = {}
        grouped_by_expiry: dict[str, dict[str, Any]] = {}

        total_unrealized = 0.0
        total_realized = 0.0
        total_margin = 0.0
        total_risk = 0.0
        for row in open_rows:
            total_unrealized += _to_float(row.unrealized_pnl)
            total_realized += _to_float(row.realized_pnl)
            total_margin += _to_float(row.margin_used)
            total_risk += _to_float(row.max_loss)

            strategy_key = row.strategy_type
            grouped_by_strategy.setdefault(strategy_key, {"count": 0, "unrealized_pnl": 0.0, "risk_exposure": 0.0})
            grouped_by_strategy[strategy_key]["count"] += 1
            grouped_by_strategy[strategy_key]["unrealized_pnl"] += _to_float(row.unrealized_pnl)
            grouped_by_strategy[strategy_key]["risk_exposure"] += _to_float(row.max_loss)

            expiry_key = row.expiry.isoformat() if row.expiry else "N/A"
            grouped_by_expiry.setdefault(expiry_key, {"count": 0, "unrealized_pnl": 0.0, "risk_exposure": 0.0})
            grouped_by_expiry[expiry_key]["count"] += 1
            grouped_by_expiry[expiry_key]["unrealized_pnl"] += _to_float(row.unrealized_pnl)
            grouped_by_expiry[expiry_key]["risk_exposure"] += _to_float(row.max_loss)

        return {
            "total_positions": len(open_rows),
            "total_unrealized_pnl": total_unrealized,
            "total_realized_pnl": total_realized,
            "total_margin_used": total_margin,
            "total_risk_exposure": total_risk,
            "by_strategy": grouped_by_strategy,
            "by_expiry": grouped_by_expiry,
        }
