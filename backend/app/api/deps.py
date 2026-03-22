from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.backtest import BacktestService
from app.services.execution_preview import ExecutionPreviewService
from app.services.market_data import MarketDataService
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
