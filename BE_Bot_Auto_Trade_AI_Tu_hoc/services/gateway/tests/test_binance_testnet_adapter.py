"""004 Binance Spot Testnet adapter — mock HTTP; no real keys/network."""

from __future__ import annotations

import json
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from gateway import account_store, alerts_store, auth_store, kill_switch_store, risk_guard
from gateway.app import app
from gateway.trading import binance_testnet, ledger
from gateway.trading.binance_testnet import BinanceTestnetError, assert_testnet_base_url
from gateway.trading.paper_adapter import VenueAdapterError, submit_and_fill

client = TestClient(app)
DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    auth_store.clear()
    account_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    ledger.clear()
    risk_guard.set_risk_available(True)
    binance_testnet.set_test_transport(None)
    monkeypatch.delenv("PAPER_VENUE_MODE", raising=False)
    monkeypatch.delenv("BINANCE_TESTNET_BASE_URL", raising=False)
    yield
    binance_testnet.set_test_transport(None)
    auth_store.clear()
    account_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    ledger.clear()


def _login() -> str:
    r = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_assert_rejects_mainnet_host() -> None:
    with pytest.raises(BinanceTestnetError) as exc:
        assert_testnet_base_url("https://api.binance.com")
    assert exc.value.code == "venue_host_rejected"


def test_assert_allows_testnet_host() -> None:
    assert assert_testnet_base_url("https://testnet.binance.vision") == (
        "https://testnet.binance.vision"
    )


def test_binance_mode_rejects_non_testnet_account(monkeypatch: pytest.MonkeyPatch) -> None:
    """Live account never uses paper testnet path — hits live gate first."""
    monkeypatch.setenv("PAPER_VENUE_MODE", "binance_testnet")
    acct = account_store.create_account(
        name="live-ish",
        exchange="binance",
        market_type="spot",
        testnet=False,
    )
    account_store.register_api_key(
        account_id=str(acct["id"]),
        label="k",
        api_key="ABCDEFGHsecret",
        api_secret="seeeeeecret",
    )
    with pytest.raises(VenueAdapterError) as exc:
        submit_and_fill(
            account_id=str(acct["id"]),
            symbol="BTCUSDT",
            side="buy",
            quantity=0.001,
            risk_check_id=str(uuid4()),
            trace_id=str(uuid4()),
        )
    assert exc.value.code == "live_trading_disabled"


def test_mock_binance_fill_updates_ledger(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPER_VENUE_MODE", "binance_testnet")

    def handler(request: httpx.Request) -> httpx.Response:
        assert "testnet.binance.vision" in str(request.url)
        assert request.headers.get("X-MBX-APIKEY")
        assert "signature=" in str(request.url)
        body = {
            "symbol": "BTCUSDT",
            "orderId": 123456,
            "status": "FILLED",
            "executedQty": "0.001",
            "cummulativeQuoteQty": "50.0",
            "fills": [{"price": "50000.0", "qty": "0.001", "commission": "0"}],
        }
        return httpx.Response(200, json=body)

    binance_testnet.set_test_transport(httpx.MockTransport(handler))
    acct = account_store.create_account(
        name="tn",
        exchange="binance",
        market_type="spot",
        testnet=True,
    )
    account_store.register_api_key(
        account_id=str(acct["id"]),
        label="k",
        api_key="ABCDEFGHsecret",
        api_secret="seeeeeecret",
    )
    result = submit_and_fill(
        account_id=str(acct["id"]),
        symbol="BTCUSDT",
        side="buy",
        quantity=0.001,
        risk_check_id=str(uuid4()),
        trace_id=str(uuid4()),
    )
    assert result["venue"] == "binance_testnet"
    assert result["fill_price"] == 50000.0
    assert result["order"]["venue_order_id"] == "123456"
    positions = ledger.list_positions(account_id=str(acct["id"]))
    assert len(positions) == 1
    assert positions[0]["quantity"] == 0.001


def test_binance_http_error_fail_closed_no_ledger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PAPER_VENUE_MODE", "binance_testnet")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(418, json={"code": -1000, "msg": "fail"})

    binance_testnet.set_test_transport(httpx.MockTransport(handler))
    acct = account_store.create_account(
        name="tn",
        exchange="binance",
        market_type="spot",
        testnet=True,
    )
    account_store.register_api_key(
        account_id=str(acct["id"]),
        label="k",
        api_key="ABCDEFGHsecret",
        api_secret="seeeeeecret",
    )
    with pytest.raises(VenueAdapterError) as exc:
        submit_and_fill(
            account_id=str(acct["id"]),
            symbol="BTCUSDT",
            side="buy",
            quantity=0.001,
            risk_check_id=str(uuid4()),
            trace_id=str(uuid4()),
        )
    assert exc.value.code == "venue_reject"
    assert ledger.list_orders(account_id=str(acct["id"])) == []


def test_activate_uses_binance_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPER_VENUE_MODE", "binance_testnet")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "orderId": 99,
                "status": "FILLED",
                "executedQty": "0.001",
                "fills": [{"price": "100.0", "qty": "0.001"}],
            },
        )

    binance_testnet.set_test_transport(httpx.MockTransport(handler))
    token = _login()
    headers = _h(token)
    acct = client.post(
        "/v1/accounts",
        headers=headers,
        json={
            "name": "bn",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    )
    assert acct.status_code == 201
    account_id = acct.json()["id"]
    key = client.post(
        f"/v1/accounts/{account_id}/api-keys",
        headers=headers,
        json={"label": "paper", "api_key": "ABCDEFGHsecret", "api_secret": "seeeeeecret"},
    )
    assert key.status_code == 201
    # Ensure secrets not echoed
    assert "seeeeeecret" not in json.dumps(key.json())

    created = client.post(
        "/v1/strategies",
        headers=headers,
        json={
            "account_id": account_id,
            "name": "s",
            "symbol": "BTCUSDT",
            "timeframe": "1m",
            "status": "draft",
        },
    )
    assert created.status_code == 201
    sid = created.json()["id"]
    patched = client.patch(
        f"/v1/strategies/{sid}",
        headers=headers,
        json={"status": "active"},
    )
    assert patched.status_code == 200
    orders = ledger.list_orders(account_id=account_id)
    assert len(orders) == 1
    assert orders[0]["venue_order_id"] == "99"


def test_default_internal_mode_ignores_binance_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default mode must not hit venue even if transport is set."""
    called = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        called["n"] += 1
        return httpx.Response(500, json={})

    binance_testnet.set_test_transport(httpx.MockTransport(handler))
    monkeypatch.delenv("PAPER_VENUE_MODE", raising=False)
    acct = account_store.create_account(
        name="tn",
        exchange="binance",
        market_type="spot",
        testnet=True,
    )
    account_store.register_api_key(
        account_id=str(acct["id"]),
        label="k",
        api_key="ABCDEFGHsecret",
        api_secret="seeeeeecret",
    )
    result = submit_and_fill(
        account_id=str(acct["id"]),
        symbol="BTCUSDT",
        side="buy",
        quantity=0.001,
        risk_check_id=str(uuid4()),
        trace_id=str(uuid4()),
    )
    assert result["venue"] == "internal"
    assert called["n"] == 0
