# Crypto Option Income Strategy System (MVP)

BTC option income strategy system with Binance-first adapter architecture.

## Quick Start (Local)

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## Docker Compose

```powershell
docker compose up --build
```

## Implemented MVP APIs

- `GET /api/market/btc`
- `GET /api/options/chain`
- `GET /api/strategies/bull-put-spreads/recommendations`
- `GET /api/strategies/bear-call-spreads/recommendations`
- `POST /api/risk/check`
- `POST /api/execution/preview`
- `POST /api/backtest/run`

New platform APIs:

- `GET /api/account/summary`
- `GET /api/account/risk`
- `GET /api/account/positions`
- `GET /api/account/pnl`
- `GET /api/account/margin`
- `GET /api/config/strategy`
- `PUT /api/config/strategy`
- `GET /api/config/risk`
- `PUT /api/config/risk`
- `GET /api/config/execution`
- `PUT /api/config/execution`
- `GET /api/market/stream-status`
- `GET /api/market/quotes/latest`
- `GET /api/options/realtime-chain`
- `GET /api/system/health`
- `GET /api/positions`
- `GET /api/positions/open`
- `GET /api/positions/closed`
- `GET /api/positions/{position_id}`
- `POST /api/positions/{position_id}/close`
- `GET /api/pnl/summary`
- `GET /api/pnl/history`
- `GET /api/pnl/by-strategy`
- `GET /api/audit/events`
- `GET /api/audit/config-history`
- `GET /api/audit/executions`
- `GET /api/audit/risk-blocks`
- `GET /api/audit/errors`
- `GET /api/trading/mode`
- `PUT /api/trading/mode`

Binance diagnostics:

- `GET /api/binance/ping`
- `GET /api/binance/account/spot`
- `GET /api/binance/account/spot/api-restrictions`
- `GET /api/binance/account/options`

## Notes

- Live order placement is disabled by default (`ENABLE_LIVE_TRADING=false`).
- `DRY_RUN` is default; `SEMI_AUTO` requires manual confirmation; `LIVE_TRADING` requires explicit enable.
- API keys are loaded from environment variables only.
- Strategy layer uses normalized domain objects and does not consume raw exchange JSON directly.
