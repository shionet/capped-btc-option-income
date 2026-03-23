from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import AccountSnapshotRecord, PositionRecord
from app.domain.enums import ExchangeName
from app.exchanges.binance.client import BinanceAuthError, BinanceRequestError, BinanceRestClient


def _as_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


class AccountService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def _binance_client(self) -> BinanceRestClient:
        return BinanceRestClient(
            base_url=self.settings.binance_base_url,
            options_base_url=self.settings.binance_options_base_url,
            timeout_seconds=self.settings.binance_timeout_seconds,
            recv_window=self.settings.binance_recv_window,
            api_key=self.settings.binance_api_key,
            api_secret=self.settings.binance_api_secret,
        )

    def _position_risk_exposure(self) -> float:
        total = self.db.query(func.sum(PositionRecord.max_loss)).filter(
            PositionRecord.status.in_(["opening", "open", "closing"])
        ).scalar()
        return _as_float(total)

    def _latest_snapshot(self, exchange: ExchangeName) -> AccountSnapshotRecord | None:
        return self.db.query(AccountSnapshotRecord).filter(
            AccountSnapshotRecord.exchange == exchange.value
        ).order_by(desc(AccountSnapshotRecord.id)).first()

    async def refresh_summary(self, exchange: ExchangeName = ExchangeName.BINANCE) -> dict[str, Any]:
        if exchange != ExchangeName.BINANCE:
            raise ValueError(f"Unsupported exchange for account summary: {exchange.value}")

        spot_data: dict[str, Any] = {}
        options_data: dict[str, Any] = {}
        source = "live"
        warnings: list[str] = []

        client = self._binance_client()
        try:
            spot_data = await client.get_spot_account_info()
            options_data = await client.get_options_account_info()
        except (BinanceAuthError, BinanceRequestError) as exc:
            source = "cache"
            warnings.append(str(exc))

        if source == "live":
            total_spot = 0.0
            available_spot = 0.0
            for row in spot_data.get("balances", []):
                free = _as_float(row.get("free"))
                locked = _as_float(row.get("locked"))
                total_spot += free + locked
                available_spot += free

            total_asset = _as_float(options_data.get("totalAsset")) or total_spot
            available_balance = _as_float(options_data.get("availableBalance")) or available_spot
            used_margin = _as_float(options_data.get("totalMaintMargin"))
            unrealized_pnl = _as_float(options_data.get("unrealizedPNL"))
            realized_pnl = _as_float(options_data.get("realizedPNL"))
            daily_pnl = _as_float(options_data.get("dailyPNL"))
            risk_exposure = self._position_risk_exposure()

            payload = {
                "spot": spot_data,
                "options": options_data,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            snapshot = AccountSnapshotRecord(
                exchange=exchange.value,
                total_asset=total_asset,
                available_balance=available_balance,
                used_margin=used_margin,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                daily_pnl=daily_pnl,
                risk_exposure=risk_exposure,
                payload_json=json.dumps(payload, ensure_ascii=True),
            )
            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)
        else:
            snapshot = self._latest_snapshot(exchange)
            if snapshot is None:
                now = datetime.now(timezone.utc).isoformat()
                return {
                    "exchange": exchange.value,
                    "source": "empty",
                    "total_account_asset": 0.0,
                    "available_balance": 0.0,
                    "used_margin": 0.0,
                    "unrealized_pnl": 0.0,
                    "realized_pnl": 0.0,
                    "daily_pnl": 0.0,
                    "risk_exposure": self._position_risk_exposure(),
                    "positions_count": 0,
                    "updated_at": now,
                    "warnings": warnings,
                }

        open_positions_count = self.db.query(func.count(PositionRecord.id)).filter(
            PositionRecord.status.in_(["opening", "open", "closing"])
        ).scalar() or 0
        return {
            "exchange": exchange.value,
            "source": source,
            "total_account_asset": _as_float(snapshot.total_asset),
            "available_balance": _as_float(snapshot.available_balance),
            "used_margin": _as_float(snapshot.used_margin),
            "unrealized_pnl": _as_float(snapshot.unrealized_pnl),
            "realized_pnl": _as_float(snapshot.realized_pnl),
            "daily_pnl": _as_float(snapshot.daily_pnl),
            "risk_exposure": _as_float(snapshot.risk_exposure),
            "positions_count": int(open_positions_count),
            "updated_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            "warnings": warnings,
        }

    def get_summary(self, exchange: ExchangeName = ExchangeName.BINANCE) -> dict[str, Any]:
        snapshot = self._latest_snapshot(exchange)
        risk_exposure = self._position_risk_exposure()
        if snapshot is None:
            return {
                "exchange": exchange.value,
                "source": "empty",
                "total_account_asset": 0.0,
                "available_balance": 0.0,
                "used_margin": 0.0,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
                "daily_pnl": 0.0,
                "risk_exposure": risk_exposure,
                "positions_count": 0,
                "updated_at": None,
            }
        open_positions_count = self.db.query(func.count(PositionRecord.id)).filter(
            PositionRecord.status.in_(["opening", "open", "closing"])
        ).scalar() or 0
        return {
            "exchange": exchange.value,
            "source": "snapshot",
            "total_account_asset": _as_float(snapshot.total_asset),
            "available_balance": _as_float(snapshot.available_balance),
            "used_margin": _as_float(snapshot.used_margin),
            "unrealized_pnl": _as_float(snapshot.unrealized_pnl),
            "realized_pnl": _as_float(snapshot.realized_pnl),
            "daily_pnl": _as_float(snapshot.daily_pnl),
            "risk_exposure": risk_exposure,
            "positions_count": int(open_positions_count),
            "updated_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        }

    def get_risk(self, exchange: ExchangeName = ExchangeName.BINANCE) -> dict[str, Any]:
        summary = self.get_summary(exchange)
        equity = max(_as_float(summary["total_account_asset"]), 1e-9)
        utilization = _as_float(summary["risk_exposure"]) / equity
        return {
            "exchange": exchange.value,
            "risk_exposure": _as_float(summary["risk_exposure"]),
            "risk_utilization": utilization,
            "max_daily_exposure_pct": self.settings.risk_max_daily_exposure_pct,
            "max_daily_loss_pct": self.settings.risk_max_daily_loss_pct,
            "is_open_allowed": utilization <= self.settings.risk_max_daily_exposure_pct,
            "updated_at": summary["updated_at"],
        }

    def get_margin(self, exchange: ExchangeName = ExchangeName.BINANCE) -> dict[str, Any]:
        summary = self.get_summary(exchange)
        total = max(_as_float(summary["total_account_asset"]), 1e-9)
        used = _as_float(summary["used_margin"])
        return {
            "exchange": exchange.value,
            "used_margin": used,
            "available_balance": _as_float(summary["available_balance"]),
            "margin_usage_ratio": used / total,
            "updated_at": summary["updated_at"],
        }

    def get_positions_snapshot(self, exchange: ExchangeName = ExchangeName.BINANCE) -> dict[str, Any]:
        rows = self.db.query(PositionRecord).filter(
            PositionRecord.exchange == exchange.value
        ).order_by(desc(PositionRecord.id)).all()
        return {
            "exchange": exchange.value,
            "count": len(rows),
            "items": [
                {
                    "position_id": row.position_uid,
                    "strategy_type": row.strategy_type,
                    "underlying": row.underlying,
                    "quantity": row.quantity,
                    "status": row.status,
                    "max_loss": _as_float(row.max_loss),
                    "unrealized_pnl": _as_float(row.unrealized_pnl),
                    "realized_pnl": _as_float(row.realized_pnl),
                    "margin_used": _as_float(row.margin_used),
                    "expiry": row.expiry.isoformat() if row.expiry else None,
                    "opened_at": row.opened_at.isoformat() if row.opened_at else None,
                }
                for row in rows
            ],
        }

    def get_pnl(self, exchange: ExchangeName = ExchangeName.BINANCE) -> dict[str, Any]:
        summary = self.get_summary(exchange)
        return {
            "exchange": exchange.value,
            "realized_pnl": _as_float(summary["realized_pnl"]),
            "unrealized_pnl": _as_float(summary["unrealized_pnl"]),
            "daily_pnl": _as_float(summary["daily_pnl"]),
            "updated_at": summary["updated_at"],
        }
