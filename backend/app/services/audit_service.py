from __future__ import annotations

import json
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import (
    AuditEventRecord,
    ConfigChangeHistoryRecord,
    ExecutionPlanRecord,
    RiskBlockRecord,
    SystemErrorRecord,
)


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record_event(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
        level: str = "INFO",
        source: str = "system",
        actor: str = "system",
    ) -> None:
        row = AuditEventRecord(
            event_type=event_type,
            event_level=level,
            source=source,
            actor=actor,
            payload_json=json.dumps(payload, ensure_ascii=True),
        )
        self.db.add(row)
        self.db.commit()

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(AuditEventRecord).order_by(desc(AuditEventRecord.id)).limit(limit).all()
        return [
            {
                "id": row.id,
                "event_type": row.event_type,
                "event_level": row.event_level,
                "source": row.source,
                "actor": row.actor,
                "payload": json.loads(row.payload_json or "{}"),
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

    def list_config_history(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(ConfigChangeHistoryRecord).order_by(desc(ConfigChangeHistoryRecord.id)).limit(limit).all()
        return [
            {
                "id": row.id,
                "domain": row.domain,
                "old_version": row.old_version,
                "new_version": row.new_version,
                "actor": row.actor,
                "reason": row.reason,
                "diff": json.loads(row.diff_json or "{}"),
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

    def list_executions(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(ExecutionPlanRecord).order_by(desc(ExecutionPlanRecord.id)).limit(limit).all()
        return [
            {
                "id": row.id,
                "plan_id": row.plan_uid,
                "strategy_id": row.strategy_id,
                "mode": row.mode,
                "status": row.status,
                "quantity": row.quantity,
                "error_message": row.error_message,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in rows
        ]

    def list_risk_blocks(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(RiskBlockRecord).order_by(desc(RiskBlockRecord.id)).limit(limit).all()
        return [
            {
                "id": row.id,
                "strategy_id": row.strategy_id,
                "reasons": json.loads(row.reasons_json or "[]"),
                "checks": json.loads(row.checks_json or "{}"),
                "metrics": json.loads(row.metrics_json or "{}"),
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

    def list_errors(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(SystemErrorRecord).order_by(desc(SystemErrorRecord.id)).limit(limit).all()
        return [
            {
                "id": row.id,
                "error_type": row.error_type,
                "message": row.message,
                "payload": json.loads(row.payload_json or "{}"),
                "resolved": row.resolved,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

    def record_error(self, error_type: str, message: str, payload: dict[str, Any] | None = None) -> None:
        row = SystemErrorRecord(
            error_type=error_type,
            message=message,
            payload_json=json.dumps(payload or {}, ensure_ascii=True),
            resolved=False,
        )
        self.db.add(row)
        self.db.commit()
