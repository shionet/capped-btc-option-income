from fastapi import APIRouter

from app.api.binance import router as binance_router
from app.api.v1.account import router as account_router
from app.api.v1.audit import router as audit_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.config import router as config_router
from app.api.v1.execution import router as execution_router
from app.api.v1.market import router as market_router
from app.api.v1.options import router as options_router
from app.api.v1.pnl import router as pnl_router
from app.api.v1.positions import router as positions_router
from app.api.v1.risk import router as risk_router
from app.api.v1.strategies import router as strategies_router
from app.api.v1.system import router as system_router
from app.api.v1.trading import router as trading_router

api_router = APIRouter()
api_router.include_router(binance_router)
api_router.include_router(account_router)
api_router.include_router(market_router)
api_router.include_router(options_router)
api_router.include_router(strategies_router)
api_router.include_router(risk_router)
api_router.include_router(execution_router)
api_router.include_router(backtest_router)
api_router.include_router(config_router)
api_router.include_router(positions_router)
api_router.include_router(pnl_router)
api_router.include_router(system_router)
api_router.include_router(audit_router)
api_router.include_router(trading_router)
