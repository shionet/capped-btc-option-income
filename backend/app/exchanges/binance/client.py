from __future__ import annotations

import asyncio
import hashlib
import hmac
import time
from typing import Any, Mapping
from urllib.parse import urlencode

import httpx


class BinanceAuthError(Exception):
    pass


class BinanceRequestError(Exception):
    def __init__(self, status_code: int, message: str, payload: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


def _parse_retry_after(headers: Mapping[str, str]) -> float:
    raw = headers.get("Retry-After")
    if not raw:
        return 0.0
    try:
        return max(float(raw), 0.0)
    except ValueError:
        return 0.0


def _extract_used_weight(headers: Mapping[str, str]) -> int | None:
    used_values: list[int] = []
    for key, value in headers.items():
        if key.upper().startswith("X-MBX-USED-WEIGHT-"):
            try:
                used_values.append(int(float(value)))
            except (TypeError, ValueError):
                continue
    if not used_values:
        return None
    return max(used_values)


class _BinanceRateGate:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._min_interval_seconds = 0.04
        self._last_request_at = 0.0
        self._soft_backoff_until = 0.0
        self._blocked_until = 0.0
        self._request_weight_limit_1m: int | None = None
        self._last_used_weight_1m: int | None = None

    async def wait_slot(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                wait_until = max(
                    self._last_request_at + self._min_interval_seconds,
                    self._soft_backoff_until,
                    self._blocked_until,
                )
                if wait_until <= now:
                    self._last_request_at = now
                    return
                sleep_for = min(max(wait_until - now, 0.0), 5.0)
            await asyncio.sleep(sleep_for)

    async def set_weight_limit_from_exchange_info(self, exchange_info: dict[str, Any]) -> None:
        limit: int | None = None
        for row in exchange_info.get("rateLimits", []):
            if (
                str(row.get("rateLimitType", "")).upper() == "REQUEST_WEIGHT"
                and str(row.get("interval", "")).upper() == "MINUTE"
                and int(row.get("intervalNum", 0) or 0) == 1
            ):
                try:
                    limit = int(row.get("limit"))
                except (TypeError, ValueError):
                    limit = None
                break
        if limit is None:
            return
        async with self._lock:
            self._request_weight_limit_1m = limit

    async def observe_headers(self, headers: Mapping[str, str]) -> None:
        used = _extract_used_weight(headers)
        if used is None:
            return
        async with self._lock:
            self._last_used_weight_1m = used
            if not self._request_weight_limit_1m:
                return
            ratio = used / max(self._request_weight_limit_1m, 1)
            now = time.monotonic()
            backoff = 0.0
            if ratio >= 0.98:
                backoff = 2.0
            elif ratio >= 0.92:
                backoff = 0.8
            elif ratio >= 0.85:
                backoff = 0.25
            if backoff > 0:
                self._soft_backoff_until = max(self._soft_backoff_until, now + backoff)

    async def trigger_limit_block(self, *, status_code: int, retry_after_seconds: float) -> float:
        now = time.monotonic()
        if status_code == 418:
            cooldown = max(retry_after_seconds, 120.0)
        else:
            cooldown = max(retry_after_seconds, 5.0)
        cooldown = min(cooldown, 3 * 24 * 3600)
        async with self._lock:
            self._blocked_until = max(self._blocked_until, now + cooldown)
        return cooldown


_GLOBAL_BINANCE_RATE_GATE = _BinanceRateGate()
_GLOBAL_OPTIONS_EXCHANGE_INFO_LOCK = asyncio.Lock()
_GLOBAL_OPTIONS_EXCHANGE_INFO_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}


class BinanceRestClient:
    def __init__(
        self,
        *,
        base_url: str,
        options_base_url: str,
        timeout_seconds: int = 12,
        recv_window: int = 5000,
        exchange_info_cache_ttl_seconds: int = 30,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.options_base_url = options_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.recv_window = recv_window
        self.exchange_info_cache_ttl_seconds = max(int(exchange_info_cache_ttl_seconds), 5)
        self.api_key = api_key
        self.api_secret = api_secret

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
            await _GLOBAL_BINANCE_RATE_GATE.wait_slot()
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

            await _GLOBAL_BINANCE_RATE_GATE.observe_headers(response.headers)
            if response.is_success:
                return response.json()

            retry_after = _parse_retry_after(response.headers)
            if response.status_code in {418, 429}:
                blocked_for = await _GLOBAL_BINANCE_RATE_GATE.trigger_limit_block(
                    status_code=response.status_code,
                    retry_after_seconds=retry_after,
                )
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
                        "blocked_for_seconds": blocked_for,
                        "url": url,
                    },
                )

            should_retry = response.status_code in {500, 502, 503, 504} and attempt < max_retry
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
        cache_key = self.options_base_url
        now = time.time()
        cached = _GLOBAL_OPTIONS_EXCHANGE_INFO_CACHE.get(cache_key)
        if cached and now - cached[0] <= self.exchange_info_cache_ttl_seconds:
            return cached[1]

        async with _GLOBAL_OPTIONS_EXCHANGE_INFO_LOCK:
            now = time.time()
            cached = _GLOBAL_OPTIONS_EXCHANGE_INFO_CACHE.get(cache_key)
            if cached and now - cached[0] <= self.exchange_info_cache_ttl_seconds:
                return cached[1]
            try:
                data = await self._request(
                    method="GET",
                    path="/eapi/v1/exchangeInfo",
                    signed=False,
                    use_options_base=True,
                )
                _GLOBAL_OPTIONS_EXCHANGE_INFO_CACHE[cache_key] = (now, data)
                await _GLOBAL_BINANCE_RATE_GATE.set_weight_limit_from_exchange_info(data)
                return data
            except BinanceRequestError as exc:
                if cached and exc.status_code in {418, 429, 500, 502, 503, 504}:
                    return cached[1]
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
