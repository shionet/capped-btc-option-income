from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import SessionLocal
from app.services.account_service import AccountService
from app.services.audit_service import AuditService
from app.services.backtest import BacktestService
from app.services.config_service import ConfigService
from app.services.execution_engine import ExecutionEngineService
from app.services.execution_preview import ExecutionPreviewService
from app.services.market_cache import MarketCacheService
from app.services.market_data import MarketDataService
from app.services.pnl_service import PnlService
from app.services.position_service import PositionService
from app.services.recommendation import RecommendationService


@lru_cache
def get_market_data_service() -> MarketDataService:
    settings: Settings = get_settings()
    return MarketDataService(settings)


@lru_cache
def get_recommendation_service() -> RecommendationService:
    settings: Settings = get_settings()
    return RecommendationService(settings)


@lru_cache
def get_execution_preview_service() -> ExecutionPreviewService:
    settings: Settings = get_settings()
    return ExecutionPreviewService(settings)


@lru_cache
def get_backtest_service() -> BacktestService:
    return BacktestService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache
def get_market_cache_service() -> MarketCacheService:
    return MarketCacheService()


def get_account_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AccountService:
    return AccountService(db, settings)


def get_config_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ConfigService:
    return ConfigService(db, settings)


def get_position_service(db: Session = Depends(get_db)) -> PositionService:
    return PositionService(db)


def get_pnl_service(db: Session = Depends(get_db)) -> PnlService:
    return PnlService(db)


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    return AuditService(db)


def get_execution_engine_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ExecutionEngineService:
    return ExecutionEngineService(db, settings)
