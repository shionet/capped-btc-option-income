from fastapi.testclient import TestClient

from app.main import app


def test_config_execution_get_and_put() -> None:
    with TestClient(app) as client:
        get_res = client.get("/api/config/execution")
        assert get_res.status_code == 200
        before = get_res.json()["data"]
        assert before["domain"] == "execution"

        put_res = client.put(
            "/api/config/execution",
            json={
                "payload": {"order_timeout_seconds": 33},
                "publish": True,
                "actor": "pytest",
                "reason": "test update",
            },
        )
        assert put_res.status_code == 200
        after = put_res.json()["data"]
        assert after["payload"]["order_timeout_seconds"] == 33


def test_trading_mode_rejects_live_when_disabled() -> None:
    with TestClient(app) as client:
        res = client.put("/api/trading/mode", json={"mode": "LIVE_TRADING", "actor": "pytest"})
        assert res.status_code == 400
        assert "ENABLE_LIVE_TRADING" in res.json()["detail"]


def test_positions_and_pnl_endpoints_available() -> None:
    with TestClient(app) as client:
        positions = client.get("/api/positions")
        assert positions.status_code == 200
        assert "items" in positions.json()

        pnl_summary = client.get("/api/pnl/summary")
        assert pnl_summary.status_code == 200
        assert "data" in pnl_summary.json()
