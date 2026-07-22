"""Binance Spot Testnet REST client — testnet hosts only; secrets never logged."""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any
from urllib.parse import urlencode, urlparse

import httpx

DEFAULT_BASE_URL = "https://testnet.binance.vision"
ALLOWED_HOST_SUFFIX = "testnet.binance.vision"


class BinanceTestnetError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def get_base_url() -> str:
    return os.environ.get("BINANCE_TESTNET_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def assert_testnet_base_url(base_url: str) -> str:
    parsed = urlparse(base_url if "://" in base_url else f"https://{base_url}")
    host = (parsed.hostname or "").lower()
    if not host or not (
        host == ALLOWED_HOST_SUFFIX or host.endswith("." + ALLOWED_HOST_SUFFIX)
    ):
        raise BinanceTestnetError(
            "venue_host_rejected",
            "Binance base URL must be Spot Testnet host (testnet.binance.vision)",
        )
    if parsed.scheme and parsed.scheme != "https":
        raise BinanceTestnetError(
            "venue_host_rejected",
            "Binance testnet base URL must use https",
        )
    return f"https://{host}"


def sign_query(secret: str, params: dict[str, Any]) -> str:
    query = urlencode(params, doseq=True)
    return hmac.new(
        secret.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _client_order_id(trace_id: str) -> str:
    # Binance newClientOrderId max length 36; keep printable ASCII.
    raw = f"t{trace_id.replace('-', '')}"
    return raw[:36]


class BinanceTestnetClient:
    """SIGNED Spot Testnet calls. Inject transport for pytest."""

    def __init__(
        self,
        *,
        api_key: str,
        api_secret: str,
        base_url: str | None = None,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = assert_testnet_base_url(base_url or get_base_url())
        self._transport = transport
        self._timeout = timeout

    def place_market_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float,
        trace_id: str,
    ) -> dict[str, Any]:
        side_u = side.upper()
        if side_u not in ("BUY", "SELL"):
            raise BinanceTestnetError("venue_validation", "side must be buy or sell")
        params: dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side_u,
            "type": "MARKET",
            "quantity": _format_qty(quantity),
            "newClientOrderId": _client_order_id(trace_id),
            "timestamp": int(time.time() * 1000),
        }
        params["signature"] = sign_query(self._api_secret, params)
        url = f"{self._base_url}/api/v3/order"
        headers = {"X-MBX-APIKEY": self._api_key}
        try:
            with httpx.Client(transport=self._transport, timeout=self._timeout) as client:
                response = client.post(url, params=params, headers=headers)
        except httpx.HTTPError as exc:
            raise BinanceTestnetError(
                "venue_unavailable",
                f"Binance testnet transport error: {exc.__class__.__name__}",
            ) from exc

        if response.status_code >= 400:
            # Do not include response body if it might echo secrets; use short code only.
            raise BinanceTestnetError(
                "venue_reject",
                f"Binance testnet rejected order (HTTP {response.status_code})",
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise BinanceTestnetError(
                "venue_reject",
                "Binance testnet returned non-JSON body",
            ) from exc
        if not isinstance(data, dict):
            raise BinanceTestnetError("venue_reject", "Binance testnet unexpected payload")
        return data


def _format_qty(quantity: float) -> str:
    # Avoid scientific notation; trim trailing zeros conservatively.
    text = f"{quantity:.8f}".rstrip("0").rstrip(".")
    return text if text else "0"


# Test seam: optional global transport override (pytest).
_test_transport: httpx.BaseTransport | None = None


def set_test_transport(transport: httpx.BaseTransport | None) -> None:
    global _test_transport
    _test_transport = transport


def get_test_transport() -> httpx.BaseTransport | None:
    return _test_transport
