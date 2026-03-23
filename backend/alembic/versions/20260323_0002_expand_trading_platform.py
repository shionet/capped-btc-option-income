"""expand trading platform models

Revision ID: 20260323_0002
Revises: 20260322_0001
Create Date: 2026-03-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260323_0002"
down_revision: Union[str, None] = "20260322_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "account_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange", sa.String(length=32), nullable=False, server_default="binance"),
        sa.Column("total_asset", sa.Float(), nullable=False, server_default="0"),
        sa.Column("available_balance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("used_margin", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unrealized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("realized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("daily_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_exposure", sa.Float(), nullable=False, server_default="0"),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "config_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("created_by", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_config_documents_domain", "config_documents", ["domain"])

    op.create_table(
        "config_effective_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain", sa.String(length=32), nullable=False, unique=True),
        sa.Column("active_config_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False, server_default="db"),
        sa.Column("effective_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "config_change_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("old_version", sa.Integer(), nullable=True),
        sa.Column("new_version", sa.Integer(), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("diff_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_config_change_history_domain", "config_change_history", ["domain"])

    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("position_uid", sa.String(length=80), nullable=False, unique=True),
        sa.Column("strategy_type", sa.String(length=50), nullable=False),
        sa.Column("underlying", sa.String(length=20), nullable=False, server_default="BTC"),
        sa.Column("exchange", sa.String(length=20), nullable=False, server_default="binance"),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("net_credit_open", sa.Float(), nullable=False, server_default="0"),
        sa.Column("current_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("realized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unrealized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("max_profit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("max_loss", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_utilization", sa.Float(), nullable=False, server_default="0"),
        sa.Column("margin_used", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expiry", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_positions_position_uid", "positions", ["position_uid"])

    op.create_table(
        "position_legs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("position_uid", sa.String(length=80), nullable=False),
        sa.Column("leg_role", sa.String(length=16), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("symbol", sa.String(length=80), nullable=False),
        sa.Column("strike", sa.Float(), nullable=False),
        sa.Column("option_type", sa.String(length=8), nullable=False),
        sa.Column("expiry", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("avg_open_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("avg_close_price", sa.Float(), nullable=True),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_position_legs_position_uid", "position_legs", ["position_uid"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_uid", sa.String(length=80), nullable=False, unique=True),
        sa.Column("position_uid", sa.String(length=80), nullable=True),
        sa.Column("plan_uid", sa.String(length=80), nullable=True),
        sa.Column("symbol", sa.String(length=80), nullable=False),
        sa.Column("leg_role", sa.String(length=16), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("order_type", sa.String(length=16), nullable=False, server_default="limit"),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("limit_price", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exchange_order_id", sa.String(length=120), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_orders_order_uid", "orders", ["order_uid"])
    op.create_index("ix_orders_plan_uid", "orders", ["plan_uid"])
    op.create_index("ix_orders_position_uid", "orders", ["position_uid"])

    op.create_table(
        "pnl_daily",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False, unique=True),
        sa.Column("realized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unrealized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("equity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("drawdown", sa.Float(), nullable=False, server_default="0"),
        sa.Column("win_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_pnl_daily_date", "pnl_daily", ["date"])

    op.create_table(
        "execution_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_uid", sa.String(length=80), nullable=False, unique=True),
        sa.Column("strategy_id", sa.String(length=255), nullable=True),
        sa.Column("mode", sa.String(length=32), nullable=False, server_default="DRY_RUN"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="planned"),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("max_slippage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("fallback_market", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_by", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_execution_plans_plan_uid", "execution_plans", ["plan_uid"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_level", sa.String(length=16), nullable=False, server_default="INFO"),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="system"),
        sa.Column("actor", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])

    op.create_table(
        "risk_blocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("strategy_id", sa.String(length=255), nullable=True),
        sa.Column("reasons_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("checks_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("metrics_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "system_errors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("error_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("system_errors")
    op.drop_table("risk_blocks")
    op.drop_index("ix_audit_events_event_type", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_execution_plans_plan_uid", table_name="execution_plans")
    op.drop_table("execution_plans")
    op.drop_index("ix_pnl_daily_date", table_name="pnl_daily")
    op.drop_table("pnl_daily")
    op.drop_index("ix_orders_position_uid", table_name="orders")
    op.drop_index("ix_orders_plan_uid", table_name="orders")
    op.drop_index("ix_orders_order_uid", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_position_legs_position_uid", table_name="position_legs")
    op.drop_table("position_legs")
    op.drop_index("ix_positions_position_uid", table_name="positions")
    op.drop_table("positions")
    op.drop_index("ix_config_change_history_domain", table_name="config_change_history")
    op.drop_table("config_change_history")
    op.drop_table("config_effective_states")
    op.drop_index("ix_config_documents_domain", table_name="config_documents")
    op.drop_table("config_documents")
    op.drop_table("account_snapshots")
