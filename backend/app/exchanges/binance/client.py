from __future__ import annotations

import asyncio
import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import httpx


class BinanceAuthError(Exception):
    pass


class BinanceRequestError(Exception):
    def __init__(self, status_code: int, message: str, payload: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class BinanceRestClient:
    def __init__(
        self,
        *,
        base_url: str,
        options_base_url: str,
        timeout_seconds: int = 12,
        recv_window: int = 5000,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.options_base_url = options_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.recv_window = recv_window
        self.api_key = api_key
        self.api_secret = api_secret
        self._options_exchange_info_cache: dict[str, Any] | None = None
        self._options_exchange_info_cached_at: float = 0.0
        self._options_exchange_info_ttl_seconds: int = 300

    def _sign(self, params: dict[str, Any]) -> str:
        if not self.api_secret:
            raise BinanceAuthError("Missing BINANCE_API_SECRET")
        query = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _build_signed_params(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = dict(params or {})
        payload["timestamp"] = int(time.time() * 1000)
        payload["recvWindow"] = self.recv_window
        payload["signature"] = self._sign(payload)
        return payload

    async def _request(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        signed: bool = False,
        use_options_base: bool = False,
    ) -> Any:
        if signed and not self.api_key:
            raise BinanceAuthError("Missing BINANCE_API_KEY")

        request_params = self._build_signed_params(params) if signed else params
        headers = {"X-MBX-APIKEY": self.api_key} if signed else None
        base_url = self.options_base_url if use_options_base else self.base_url
        url = f"{base_url}{path}"

        max_retry = 2
        for attempt in range(max_retry + 1):
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                try:
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        params=request_params,
                        headers=headers,
                    )
                except httpx.HTTPError as exc:
                    if attempt >= max_retry:
                        raise BinanceRequestError(
                            status_code=0,
                            message=f"Binance network error: {exc}",
                            payload={"url": url},
                        ) from exc
                    await asyncio.sleep(0.35 * (attempt + 1))
                    continue

            if response.is_success:
                return response.json()

            retry_after = 0.0
            try:
                retry_after = float(response.headers.get("Retry-After", "0"))
            except ValueError:
                retry_after = 0.0
            should_retry = response.status_code in {418, 429, 500, 502, 503, 504} and attempt < max_retry
            if should_retry:
                await asyncio.sleep(max(retry_after, 0.35 * (attempt + 1)))
                continue

            try:
                payload = response.json()
            except Exception:
                payload = {"text": response.text}
            raise BinanceRequestError(
                status_code=response.status_code,
                message=f"Binance request failed: {response.status_code}",
                payload={
                    "body": payload,
                    "retry_after": response.headers.get("Retry-After"),
                    "url": url,
                },
            )

        raise BinanceRequestError(status_code=0, message="Unexpected request retry failure", payload={"url": url})

    async def get_server_time(self) -> dict[str, Any]:
        return await self._request(method="GET", path="/api/v3/time", signed=False)

    async def get_spot_ticker_price(self, symbol: str) -> dict[str, Any]:
        return await self._request(method="GET", path="/api/v3/ticker/price", params={"symbol": symbol}, signed=False)

    async def get_options_exchange_info(self) -> dict[str, Any]:
        now = time.time()
        if (
            self._options_exchange_info_cache is not None
            and now - self._options_exchange_info_cached_at <= self._options_exchange_info_ttl_seconds
        ):
            return self._options_exchange_info_cache
        try:
            data = await self._request(
                method="GET",
                path="/eapi/v1/exchangeInfo",
                signed=False,
                use_options_base=True,
            )
            self._options_exchange_info_cache = data
            self._options_exchange_info_cached_at = now
            return data
        except BinanceRequestError as exc:
            if self._options_exchange_info_cache is not None and exc.status_code in {418, 429, 500, 502, 503, 504}:
                return self._options_exchange_info_cache
            raise

    async def get_options_ticker(self) -> list[dict[str, Any]]:
        return await self._request(
            method="GET",
            path="/eapi/v1/ticker",
            signed=False,
            use_options_base=True,
        )

    async def get_options_mark(self) -> list[dict[str, Any]]:
        return await self._request(
            method="GET",
            path="/eapi/v1/mark",
            signed=False,
            use_options_base=True,
        )

    async def get_spot_account_info(self) -> dict[str, Any]:
        return await self._request(
            method="GET",
            path="/api/v3/account",
            signed=True,
        )

    async def get_spot_api_restrictions(self) -> dict[str, Any]:
        return await self._request(
            method="GET",
            path="/sapi/v1/account/apiRestrictions",
            signed=True,
        )

    async def get_options_account_info(self) -> dict[str, Any]:
        return await self._request(
            method="GET",
            path="/eapi/v1/marginAccount",
            signed=True,
            use_options_base=True,
        )
