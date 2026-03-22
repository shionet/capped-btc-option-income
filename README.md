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

Binance diagnostics:

- `GET /api/binance/ping`
- `GET /api/binance/account/spot`
- `GET /api/binance/account/spot/api-restrictions`
- `GET /api/binance/account/options`

## Notes

- Live order placement is disabled by default (`TRADING_LIVE_ENABLED=false`).
- API keys are loaded from environment variables only.
- Strategy layer uses normalized domain objects and does not consume raw exchange JSON directly.
