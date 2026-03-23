from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import ConfigChangeHistoryRecord, ConfigDocumentRecord, ConfigEffectiveStateRecord
from app.domain.enums import ConfigDomain, RunMode


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class ConfigService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def default_payload(self, domain: ConfigDomain) -> dict[str, Any]:
        if domain == ConfigDomain.STRATEGY:
            return {
                "base": {
                    "underlying": self.settings.strategy_underlying,
                    "allowed_exchanges": sorted(self.settings.allowed_exchanges_values()),
                    "allowed_dte_min": self.settings.strategy_allowed_dte_min,
                    "allowed_dte_max": self.settings.strategy_allowed_dte_max,
                    "candidate_limit": self.settings.strategy_candidate_limit,
                    "min_daily_return_on_risk": 0.0,
                    "min_annualized_return_on_risk": 0.0,
                    "score_dte_weight": 1.0,
                },
                "bull_put_spread": {
                    "sell_otm_min_pct": self.settings.strategy_bull_put_sell_otm_min_pct,
                    "sell_otm_max_pct": self.settings.strategy_bull_put_sell_otm_max_pct,
                    "buy_wing_min_pct": self.settings.strategy_bull_put_buy_wing_min_pct,
                    "buy_wing_max_pct": self.settings.strategy_bull_put_buy_wing_max_pct,
                    "min_net_premium": self.settings.strategy_bull_put_min_net_premium,
                    "min_reward_risk": self.settings.strategy_bull_put_min_reward_risk,
                    "max_width": self.settings.strategy_bull_put_max_width,
                },
                "bear_call_spread": {
                    "sell_otm_min_pct": self.settings.strategy_bear_call_sell_otm_min_pct,
                    "sell_otm_max_pct": self.settings.strategy_bear_call_sell_otm_max_pct,
                    "buy_wing_min_pct": self.settings.strategy_bear_call_buy_wing_min_pct,
                    "buy_wing_max_pct": self.settings.strategy_bear_call_buy_wing_max_pct,
                    "min_net_premium": self.settings.strategy_bear_call_min_net_premium,
                    "min_reward_risk": self.settings.strategy_bear_call_min_reward_risk,
                    "max_width": self.settings.strategy_bear_call_max_width,
                },
                "iv": {
                    "enabled": self.settings.iv_filter_enabled,
                    "min_iv": self.settings.iv_min,
                    "max_iv": self.settings.iv_max,
                    "min_percentile": self.settings.iv_min_percentile,
                    "window_minutes": self.settings.iv_window_minutes,
                },
                "liquidity": {
                    "min_bid": self.settings.liquidity_min_bid,
                    "min_ask_depth": self.settings.liquidity_min_ask_depth,
                    "max_bid_ask_spread": self.settings.liquidity_max_bid_ask_spread,
                    "min_activity": self.settings.liquidity_min_activity,
                },
            }
        if domain == ConfigDomain.RISK:
            return {
                "max_single_trade_loss_pct": self.settings.risk_max_single_trade_loss_pct,
                "max_daily_exposure_pct": self.settings.risk_max_daily_exposure_pct,
                "max_daily_loss_pct": self.settings.risk_max_daily_loss_pct,
                "max_positions": self.settings.risk_max_positions,
                "max_same_direction_positions": self.settings.risk_max_same_direction_positions,
                "consecutive_loss_pause_threshold": self.settings.risk_consecutive_loss_pause_threshold,
            }
        return {
            "enabled": self.settings.trading_enabled,
            "default_mode": self.settings.trading_default_mode,
            "order_timeout_seconds": self.settings.execution_leg_timeout_seconds,
            "max_retries": self.settings.execution_max_retries,
            "max_slippage": self.settings.execution_max_slippage,
            "allow_market_fallback": self.settings.execution_market_fallback_enabled,
            "auto_close": {
                "enabled": self.settings.auto_close_enabled,
                "alert_only": self.settings.auto_close_alert_only,
                "take_profit_pct": self.settings.auto_close_take_profit_pct,
                "stop_loss_pct": self.settings.auto_close_stop_loss_pct,
                "close_before_expiry_minutes": self.settings.auto_close_before_expiry_minutes,
            },
            "runtime": {
                "current_mode": RunMode.DRY_RUN.value,
            },
        }

    def _checksum(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _next_version(self, domain: ConfigDomain) -> int:
        max_version = self.db.query(func.max(ConfigDocumentRecord.version)).filter(
            ConfigDocumentRecord.domain == domain.value
        ).scalar()
        return int(max_version or 0) + 1

    def _payload_from_doc(self, doc: ConfigDocumentRecord | None, defaults: dict[str, Any]) -> dict[str, Any]:
        if not doc:
            return defaults
        try:
            override = json.loads(doc.payload_json)
        except json.JSONDecodeError:
            override = {}
        if not isinstance(override, dict):
            override = {}
        return _deep_merge(defaults, override)

    def _validate_payload(self, domain: ConfigDomain, payload: dict[str, Any]) -> None:
        if domain == ConfigDomain.STRATEGY:
            base = payload.get("base", {})
            if isinstance(base, dict):
                if int(base.get("candidate_limit", 1)) < 1:
                    raise ValueError("strategy.base.candidate_limit must be >= 1")
                dte_weight = float(base.get("score_dte_weight", 1.0))
                if dte_weight < 0:
                    raise ValueError("strategy.base.score_dte_weight must be >= 0")
                min_daily = float(base.get("min_daily_return_on_risk", 0.0))
                min_annualized = float(base.get("min_annualized_return_on_risk", 0.0))
                if min_daily < 0 or min_annualized < 0:
                    raise ValueError("strategy.base minimum return thresholds must be >= 0")
            return
        if domain == ConfigDomain.RISK:
            keys = ["max_single_trade_loss_pct", "max_daily_exposure_pct", "max_daily_loss_pct"]
            for key in keys:
                value = payload.get(key)
                if value is None:
                    continue
                if not 0 <= float(value) <= 1:
                    raise ValueError(f"risk.{key} must be between 0 and 1")
            return

        default_mode = str(payload.get("default_mode", "")).upper()
        if default_mode and default_mode not in {mode.value for mode in RunMode}:
            raise ValueError("execution.default_mode must be one of DRY_RUN/SEMI_AUTO/LIVE_TRADING")
        if default_mode == RunMode.LIVE_TRADING.value and not self.settings.live_trading_permitted():
            raise ValueError("LIVE_TRADING requires ENABLE_LIVE_TRADING=true")

    def _bootstrap_default_if_missing(self, domain: ConfigDomain) -> ConfigDocumentRecord:
        existing_active = self.db.query(ConfigEffectiveStateRecord).filter(
            ConfigEffectiveStateRecord.domain == domain.value
        ).first()
        if existing_active:
            doc = self.db.query(ConfigDocumentRecord).filter(
                ConfigDocumentRecord.id == existing_active.active_config_id
            ).first()
            if doc:
                return doc

        defaults = self.default_payload(domain)
        now = datetime.now(timezone.utc)
        doc = ConfigDocumentRecord(
            domain=domain.value,
            version=self._next_version(domain),
            status="active",
            payload_json=json.dumps(defaults, ensure_ascii=True),
            checksum=self._checksum(defaults),
            created_by="system",
            published_at=now,
        )
        self.db.add(doc)
        self.db.flush()
        state = self.db.query(ConfigEffectiveStateRecord).filter(
            ConfigEffectiveStateRecord.domain == domain.value
        ).first()
        if state:
            state.active_config_id = doc.id
            state.source = "default"
            state.effective_at = now
        else:
            state = ConfigEffectiveStateRecord(
                domain=domain.value,
                active_config_id=doc.id,
                source="default",
                effective_at=now,
            )
            self.db.add(state)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_config(self, domain: ConfigDomain) -> dict[str, Any]:
        active_doc = self._bootstrap_default_if_missing(domain)
        defaults = self.default_payload(domain)
        effective_payload = self._payload_from_doc(active_doc, defaults)
        state = self.db.query(ConfigEffectiveStateRecord).filter(
            ConfigEffectiveStateRecord.domain == domain.value
        ).first()
        return {
            "domain": domain.value,
            "version": active_doc.version,
            "status": active_doc.status,
            "source": state.source if state else "db",
            "effective_at": state.effective_at.isoformat() if state and state.effective_at else None,
            "updated_at": active_doc.created_at.isoformat() if active_doc.created_at else None,
            "payload": effective_payload,
        }

    def update_config(
        self,
        *,
        domain: ConfigDomain,
        payload: dict[str, Any],
        actor: str,
        publish: bool = True,
        reason: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        self._validate_payload(domain, payload)

        current = self.get_config(domain)
        new_version = self._next_version(domain)
        now = datetime.now(timezone.utc)
        status = "active" if publish else "draft"
        merged_payload = _deep_merge(current["payload"], payload)
        doc = ConfigDocumentRecord(
            domain=domain.value,
            version=new_version,
            status=status,
            payload_json=json.dumps(merged_payload, ensure_ascii=True),
            checksum=self._checksum(merged_payload),
            created_by=actor,
            published_at=now if publish else None,
        )
        self.db.add(doc)
        self.db.flush()

        if publish:
            state = self.db.query(ConfigEffectiveStateRecord).filter(
                ConfigEffectiveStateRecord.domain == domain.value
            ).first()
            if state:
                state.active_config_id = doc.id
                state.source = "db"
                state.effective_at = now
            else:
                state = ConfigEffectiveStateRecord(
                    domain=domain.value,
                    active_config_id=doc.id,
                    source="db",
                    effective_at=now,
                )
                self.db.add(state)

            history = ConfigChangeHistoryRecord(
                domain=domain.value,
                old_version=current["version"],
                new_version=new_version,
                actor=actor,
                reason=reason,
                diff_json=json.dumps(payload, ensure_ascii=True),
            )
            self.db.add(history)

        self.db.commit()
        if publish:
            return self.get_config(domain)
        return {
            "domain": domain.value,
            "version": new_version,
            "status": "draft",
            "source": "db",
            "effective_at": current["effective_at"],
            "updated_at": now.isoformat(),
            "payload": merged_payload,
        }

    def list_change_history(self, domain: ConfigDomain | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = self.db.query(ConfigChangeHistoryRecord)
        if domain:
            query = query.filter(ConfigChangeHistoryRecord.domain == domain.value)
        rows = query.order_by(desc(ConfigChangeHistoryRecord.id)).limit(limit).all()
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
