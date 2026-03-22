from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
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
