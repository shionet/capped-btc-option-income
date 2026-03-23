from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import ExecutionPlanRecord, OrderRecord
from app.domain.enums import ConfigDomain, RunMode
from app.services.config_service import ConfigService


class ExecutionEngineService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.config_service = ConfigService(db, settings)

    def get_current_mode(self) -> dict[str, Any]:
        execution = self.config_service.get_config(ConfigDomain.EXECUTION)
        runtime = execution["payload"].get("runtime", {})
        configured_mode = runtime.get("current_mode") or execution["payload"].get("default_mode", RunMode.DRY_RUN.value)
        mode = configured_mode if configured_mode in {m.value for m in RunMode} else RunMode.DRY_RUN.value
        live_permitted = self.settings.live_trading_permitted()
        if mode == RunMode.LIVE_TRADING.value and not live_permitted:
            mode = RunMode.DRY_RUN.value
        return {
            "mode": mode,
            "live_trading_enabled": live_permitted,
            "execution_config_version": execution["version"],
            "updated_at": execution["effective_at"],
        }

    def set_current_mode(self, mode: RunMode, actor: str = "user") -> dict[str, Any]:
        if mode == RunMode.LIVE_TRADING and not self.settings.live_trading_permitted():
            raise ValueError("LIVE_TRADING requires ENABLE_LIVE_TRADING=true")
        updated = self.config_service.update_config(
            domain=ConfigDomain.EXECUTION,
            payload={"runtime": {"current_mode": mode.value}},
            actor=actor,
            publish=True,
            reason="manual mode switch",
        )
        return {
            "mode": updated["payload"].get("runtime", {}).get("current_mode", RunMode.DRY_RUN.value),
            "live_trading_enabled": self.settings.live_trading_permitted(),
            "execution_config_version": updated["version"],
            "updated_at": updated["effective_at"],
        }

    def create_execution_plan(
        self,
        *,
        strategy_id: str,
        mode: RunMode,
        quantity: int,
        max_slippage: float,
        max_retries: int,
        timeout_seconds: int,
        fallback_market: bool,
        actor: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if mode == RunMode.LIVE_TRADING and not self.settings.live_trading_permitted():
            raise ValueError("LIVE_TRADING requires ENABLE_LIVE_TRADING=true")
        plan_uid = f"plan_{uuid.uuid4().hex[:12]}"
        plan = ExecutionPlanRecord(
            plan_uid=plan_uid,
            strategy_id=strategy_id,
            mode=mode.value,
            status="waiting_confirm" if mode == RunMode.SEMI_AUTO else "planned",
            quantity=quantity,
            max_slippage=max_slippage,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            fallback_market=fallback_market,
            payload_json=json.dumps(payload or {}, ensure_ascii=True),
            created_by=actor,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return self._serialize_plan(plan)

    def confirm_plan(self, plan_uid: str) -> dict[str, Any] | None:
        plan = self.db.query(ExecutionPlanRecord).filter(ExecutionPlanRecord.plan_uid == plan_uid).first()
        if not plan:
            return None
        if plan.mode == RunMode.SEMI_AUTO.value and plan.status == "waiting_confirm":
            plan.status = "confirmed"
        elif plan.mode == RunMode.DRY_RUN.value:
            plan.status = "simulated"
        else:
            plan.status = "submitted"
        plan.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(plan)
        return self._serialize_plan(plan)

    def cancel_plan(self, plan_uid: str, reason: str | None = None) -> dict[str, Any] | None:
        plan = self.db.query(ExecutionPlanRecord).filter(ExecutionPlanRecord.plan_uid == plan_uid).first()
        if not plan:
            return None
        plan.status = "cancelled"
        plan.error_message = reason
        plan.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(plan)
        return self._serialize_plan(plan)

    def monitor(self, limit: int = 50) -> dict[str, Any]:
        plans = self.db.query(ExecutionPlanRecord).order_by(desc(ExecutionPlanRecord.id)).limit(limit).all()
        orders = self.db.query(OrderRecord).order_by(desc(OrderRecord.id)).limit(limit).all()
        failed_plans = [plan for plan in plans if plan.status in {"failed", "cancelled"}]
        return {
            "recent_plans": [self._serialize_plan(plan) for plan in plans],
            "recent_orders": [
                {
                    "order_id": row.order_uid,
                    "plan_id": row.plan_uid,
                    "position_id": row.position_uid,
                    "symbol": row.symbol,
                    "leg_role": row.leg_role,
                    "side": row.side,
                    "status": row.status,
                    "retry_count": row.retry_count,
                    "error_message": row.error_message,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                }
                for row in orders
            ],
            "failed_count": len(failed_plans),
            "auto_trading_status": self.get_current_mode(),
        }

    def _serialize_plan(self, plan: ExecutionPlanRecord) -> dict[str, Any]:
        return {
            "plan_id": plan.plan_uid,
            "strategy_id": plan.strategy_id,
            "mode": plan.mode,
            "status": plan.status,
            "quantity": plan.quantity,
            "max_slippage": plan.max_slippage,
            "max_retries": plan.max_retries,
            "timeout_seconds": plan.timeout_seconds,
            "fallback_market": plan.fallback_market,
            "error_message": plan.error_message,
            "payload": json.loads(plan.payload_json or "{}"),
            "created_by": plan.created_by,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
        }
