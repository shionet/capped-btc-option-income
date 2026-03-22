from fastapi import APIRouter

from app.api.binance import router as binance_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.execution import router as execution_router
from app.api.v1.market import router as market_router
from app.api.v1.options import router as options_router
from app.api.v1.risk import router as risk_router
from app.api.v1.strategies import router as strategies_router

api_router = APIRouter()
api_router.include_router(binance_router)
api_router.include_router(market_router)
api_router.include_router(options_router)
api_router.include_router(strategies_router)
api_router.include_router(risk_router)
api_router.include_router(execution_router)
api_router.include_router(backtest_router)
