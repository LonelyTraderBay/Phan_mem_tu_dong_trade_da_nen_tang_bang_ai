"""API tests for paper market visibility stubs (P1-BE-05)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway import auth_store
from gateway.app import app
from gateway.routers.market import STALE_HEADER

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset_auth() -> None:
    auth_store.clear()
    yield
    auth_store.clear()


def _assert_error_shape(payload: dict) -> None:
    assert "code" in payload
    assert "message" in payload
    assert "trace_id" in payload
    assert isinstance(payload.get("details", []), list)


def _login_access() -> str:
    response = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_get_market_symbols_requires_auth() -> None:
    response = client.get("/v1/market/symbols")
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_get_market_candles_requires_auth() -> None:
    response = client.get(
        "/v1/market/candles",
        params={"symbol": "BTCUSDT", "interval": "1h"},
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_get_market_symbols_fixture_and_stale_header() -> None:
    token = _login_access()
    response = client.get("/v1/market/symbols", headers=_auth_headers(token))
    assert response.status_code == 200
    assert response.headers.get(STALE_HEADER) == "true"
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    row = body[0]
    assert set(row.keys()) >= {
        "symbol",
        "base_asset",
        "quote_asset",
        "exchange",
        "market_type",
        "active",
    }
    assert row["market_type"] in ("spot", "futures")


def test_get_market_symbols_filter_exchange_and_type() -> None:
    token = _login_access()
    response = client.get(
        "/v1/market/symbols",
        headers=_auth_headers(token),
        params={"exchange": "binance", "market_type": "spot"},
    )
    assert response.status_code == 200
    assert response.headers.get(STALE_HEADER) == "true"
    body = response.json()
    assert body
    assert all(r["exchange"] == "binance" and r["market_type"] == "spot" for r in body)


def test_get_market_candles_fixture_and_stale_header() -> None:
    token = _login_access()
    response = client.get(
        "/v1/market/candles",
        headers=_auth_headers(token),
        params={"symbol": "BTCUSDT", "interval": "1h", "limit": 10},
    )
    assert response.status_code == 200
    assert response.headers.get(STALE_HEADER) == "true"
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 10
    candle = body[0]
    assert set(candle.keys()) >= {
        "symbol",
        "interval",
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
    }
    assert candle["symbol"] == "BTCUSDT"
    assert candle["interval"] == "1h"
    assert candle["high"] >= candle["low"]
    assert candle["volume"] >= 0


def test_get_market_candles_unknown_symbol_empty_stale() -> None:
    token = _login_access()
    response = client.get(
        "/v1/market/candles",
        headers=_auth_headers(token),
        params={"symbol": "UNKNOWNXYZ", "interval": "5m"},
    )
    assert response.status_code == 200
    assert response.headers.get(STALE_HEADER) == "true"
    assert response.json() == []
