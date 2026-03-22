# Crypto Option Income Backend (MVP)

## Setup

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`:

```dotenv
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
TRADING_LIVE_ENABLED=false
```

## Run

```powershell
uvicorn app.main:app --reload --port 8000
```

## DB migration

```powershell
alembic upgrade head
```

## Core APIs (MVP)

- `GET /api/market/btc`
- `GET /api/options/chain?exchange=binance&expiry=YYYY-MM-DD`
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

## One-shot Binance account test

```powershell
python scripts/test_binance_account.py
```

## Tests

```powershell
python -m pytest -q tests
```
