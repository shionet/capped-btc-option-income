from fastapi.testclient import TestClient

from app.api.deps import get_recommendation_service
from app.exchanges.binance.client import BinanceRequestError
from app.main import app


class _RateLimitedRecommendationService:
    async def recommend(self, **kwargs):  # type: ignore[no-untyped-def]
        raise BinanceRequestError(status_code=429, message="rate limited", payload={})


def test_strategy_endpoint_returns_429_instead_of_500_on_rate_limit() -> None:
    app.dependency_overrides[get_recommendation_service] = lambda: _RateLimitedRecommendationService()
    try:
        with TestClient(app) as client:
            res = client.get("/api/strategies/bull-put-spreads/recommendations?exchange=binance&limit=5")
            assert res.status_code == 429
            detail = res.json()["detail"]
            assert "rate-limited" in detail["message"]
    finally:
        app.dependency_overrides.clear()
