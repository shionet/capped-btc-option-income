import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.exchanges.binance.client import BinanceAuthError, BinanceRequestError, BinanceRestClient


async def main() -> None:
    load_dotenv()

    client = BinanceRestClient(
        base_url=os.getenv("BINANCE_BASE_URL", "https://api.binance.com"),
        options_base_url=os.getenv("BINANCE_OPTIONS_BASE_URL", "https://eapi.binance.com"),
        timeout_seconds=int(os.getenv("BINANCE_TIMEOUT_SECONDS", "12")),
        recv_window=int(os.getenv("BINANCE_RECV_WINDOW", "5000")),
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
    )

    print("1) Ping Binance server time...")
    server_time = await client.get_server_time()
    print(json.dumps(server_time, indent=2))

    print("\n2) Fetch spot account...")
    try:
        spot = await client.get_spot_account_info()
        print(
            json.dumps(
                {
                    "accountType": spot.get("accountType"),
                    "canTrade": spot.get("canTrade"),
                    "updateTime": spot.get("updateTime"),
                    "balancesCount": len(spot.get("balances", [])),
                },
                indent=2,
            )
        )
    except (BinanceAuthError, BinanceRequestError) as exc:
        print(f"spot account failed: {exc}")
        if isinstance(exc, BinanceRequestError):
            print(json.dumps(exc.payload, indent=2))

    print("\n3) Fetch API restrictions...")
    try:
        restrictions = await client.get_spot_api_restrictions()
        print(json.dumps(restrictions, indent=2))
    except (BinanceAuthError, BinanceRequestError) as exc:
        print(f"api restrictions failed: {exc}")
        if isinstance(exc, BinanceRequestError):
            print(json.dumps(exc.payload, indent=2))

    print("\n4) Fetch options margin account...")
    try:
        options = await client.get_options_account_info()
        print(json.dumps(options, indent=2))
    except (BinanceAuthError, BinanceRequestError) as exc:
        print(f"options account failed: {exc}")
        if isinstance(exc, BinanceRequestError):
            print(json.dumps(exc.payload, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
