from __future__ import annotations

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class StrategyRecord(Base):
    __tablename__ = "strategy_records"

    id = Column(Integer, primary_key=True, index=True)
    strategy_type = Column(String(50), nullable=False)
    payload_json = Column(Text, nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PositionSnapshotRecord(Base):
    __tablename__ = "position_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(120), nullable=True)
    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class BacktestResultRecord(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    strategy_type = Column(String(50), nullable=False)
    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AccountSnapshotRecord(Base):
    __tablename__ = "account_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String(32), nullable=False, default="binance")
    total_asset = Column(Float, nullable=False, default=0.0)
    available_balance = Column(Float, nullable=False, default=0.0)
    used_margin = Column(Float, nullable=False, default=0.0)
    unrealized_pnl = Column(Float, nullable=False, default=0.0)
    realized_pnl = Column(Float, nullable=False, default=0.0)
    daily_pnl = Column(Float, nullable=False, default=0.0)
    risk_exposure = Column(Float, nullable=False, default=0.0)
    payload_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ConfigDocumentRecord(Base):
    __tablename__ = "config_documents"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(32), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    status = Column(String(16), nullable=False, default="draft")
    payload_json = Column(Text, nullable=False)
    checksum = Column(String(64), nullable=False, default="")
    created_by = Column(String(120), nullable=False, default="system")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)


class ConfigEffectiveStateRecord(Base):
    __tablename__ = "config_effective_states"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(32), nullable=False, unique=True)
    active_config_id = Column(Integer, nullable=False)
    source = Column(String(16), nullable=False, default="db")
    effective_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ConfigChangeHistoryRecord(Base):
    __tablename__ = "config_change_history"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(32), nullable=False, index=True)
    old_version = Column(Integer, nullable=True)
    new_version = Column(Integer, nullable=False)
    actor = Column(String(120), nullable=False, default="system")
    reason = Column(String(255), nullable=True)
    diff_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PositionRecord(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    position_uid = Column(String(80), nullable=False, unique=True, index=True)
    strategy_type = Column(String(50), nullable=False)
    underlying = Column(String(20), nullable=False, default="BTC")
    exchange = Column(String(20), nullable=False, default="binance")
    quantity = Column(Integer, nullable=False, default=1)
    net_credit_open = Column(Float, nullable=False, default=0.0)
    current_value = Column(Float, nullable=False, default=0.0)
    realized_pnl = Column(Float, nullable=False, default=0.0)
    unrealized_pnl = Column(Float, nullable=False, default=0.0)
    max_profit = Column(Float, nullable=False, default=0.0)
    max_loss = Column(Float, nullable=False, default=0.0)
    risk_utilization = Column(Float, nullable=False, default=0.0)
    margin_used = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="open")
    opened_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    expiry = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PositionLegRecord(Base):
    __tablename__ = "position_legs"

    id = Column(Integer, primary_key=True, index=True)
    position_uid = Column(String(80), nullable=False, index=True)
    leg_role = Column(String(16), nullable=False)
    side = Column(String(8), nullable=False)
    symbol = Column(String(80), nullable=False)
    strike = Column(Float, nullable=False)
    option_type = Column(String(8), nullable=False)
    expiry = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    avg_open_price = Column(Float, nullable=False, default=0.0)
    avg_close_price = Column(Float, nullable=True)
    state = Column(String(20), nullable=False, default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class OrderRecord(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_uid = Column(String(80), nullable=False, unique=True, index=True)
    position_uid = Column(String(80), nullable=True, index=True)
    plan_uid = Column(String(80), nullable=True, index=True)
    symbol = Column(String(80), nullable=False)
    leg_role = Column(String(16), nullable=False)
    side = Column(String(8), nullable=False)
    order_type = Column(String(16), nullable=False, default="limit")
    quantity = Column(Integer, nullable=False, default=1)
    limit_price = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="new")
    retry_count = Column(Integer, nullable=False, default=0)
    exchange_order_id = Column(String(120), nullable=True)
    error_code = Column(String(80), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PnlDailyRecord(Base):
    __tablename__ = "pnl_daily"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    realized_pnl = Column(Float, nullable=False, default=0.0)
    unrealized_pnl = Column(Float, nullable=False, default=0.0)
    total_pnl = Column(Float, nullable=False, default=0.0)
    equity = Column(Float, nullable=False, default=0.0)
    drawdown = Column(Float, nullable=False, default=0.0)
    win_rate = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ExecutionPlanRecord(Base):
    __tablename__ = "execution_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_uid = Column(String(80), nullable=False, unique=True, index=True)
    strategy_id = Column(String(255), nullable=True)
    mode = Column(String(32), nullable=False, default="DRY_RUN")
    status = Column(String(20), nullable=False, default="planned")
    quantity = Column(Integer, nullable=False, default=1)
    max_slippage = Column(Float, nullable=False, default=0.0)
    max_retries = Column(Integer, nullable=False, default=0)
    timeout_seconds = Column(Integer, nullable=False, default=20)
    fallback_market = Column(Boolean, nullable=False, default=False)
    error_message = Column(Text, nullable=True)
    payload_json = Column(Text, nullable=False, default="{}")
    created_by = Column(String(120), nullable=False, default="system")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    event_level = Column(String(16), nullable=False, default="INFO")
    source = Column(String(64), nullable=False, default="system")
    actor = Column(String(120), nullable=False, default="system")
    payload_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RiskBlockRecord(Base):
    __tablename__ = "risk_blocks"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String(255), nullable=True)
    reasons_json = Column(Text, nullable=False, default="[]")
    checks_json = Column(Text, nullable=False, default="{}")
    metrics_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SystemErrorRecord(Base):
    __tablename__ = "system_errors"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(64), nullable=False)
    message = Column(Text, nullable=False)
    payload_json = Column(Text, nullable=False, default="{}")
    resolved = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
