from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.deps import get_market_cache_service
from app.core.config import Settings, get_settings
from app.services.market_cache import MarketCacheService

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def system_health(
    settings: Settings = Depends(get_settings),
    cache: MarketCacheService = Depends(get_market_cache_service),
) -> dict:
    stream = cache.stream_status()
    status = "ok" if stream["exchange_connected"] or settings.app_env == "dev" else "degraded"
    return {
        "ok": True,
        "status": status,
        "env": settings.app_env,
        "mode_live_enabled": settings.live_trading_permitted(),
        "stream": stream,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
