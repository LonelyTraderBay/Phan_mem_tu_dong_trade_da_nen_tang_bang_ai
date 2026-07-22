"""013 LIVE-VENUE-ADAPTER — Binance mainnet mock HTTP; no real keys/network."""

from __future__ import annotations

from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from gateway import (
    account_store,
    alerts_store,
    auth_store,
    kill_switch_store,
    risk_guard,
    strategy_store,
)
from gateway.app import app
from gateway.trading import binance_mainnet, ledger
from gateway.trading.binance_mainnet import (
    BinanceMainnetError,
    assert_mainnet_base_url,
)

client = TestClient(app)
DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    ledger.clear()
    risk_guard.set_risk_available(True)
    binance_mainnet.set_test_transport(None)
    for key in (
        "LIVE_TRADING_ENABLED",
        "PHASE2_GATES_ACK",
        "LIVE_NAV_QUOTE",
        "LIVE_MAX_NAV_PCT",
        "LIVE_VENUE_MODE",
        "BINANCE_MAINNET_BASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)
    yield
    binance_mainnet.set_test_transport(None)
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
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


def test_assert_rejects_testnet_host() -> None:
    with pytest.raises(BinanceMainnetError) as exc:
        assert_mainnet_base_url("https://testnet.binance.vision")
    assert exc.value.code == "venue_host_rejected"


def test_assert_allows_mainnet_host() -> None:
    assert assert_mainnet_base_url("https://api.binance.com") == (
        "https://api.binance.com"
    )


def test_live_activate_mock_fill_within_nav_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "true")
    monkeypatch.setenv("PHASE2_GATES_ACK", "true")
    monkeypatch.setenv("LIVE_NAV_QUOTE", "100000")
    monkeypatch.setenv("LIVE_MAX_NAV_PCT", "5")
    monkeypatch.setenv("LIVE_VENUE_MODE", "binance_mainnet")

    def handler(request: httpx.Request) -> httpx.Response:
        assert "api.binance.com" in str(request.url)
        assert "testnet" not in str(request.url)
        body = {
            "orderId": 42,
            "status": "FILLED",
            "executedQty": "0.001",
            "cummulativeQuoteQty": "100.0",
            "fills": [{"qty": "0.001", "price": "100000"}],
        }
        # notional 100 << 5000 cap
        return httpx.Response(200, json=body)

    binance_mainnet.set_test_transport(httpx.MockTransport(handler))

    token = _login()
    acct = client.post(
        "/v1/accounts",
        headers=_h(token),
        json={
            "name": "live",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": False,
        },
    )
    account_id = acct.json()["id"]
    client.post(
        f"/v1/accounts/{account_id}/api-keys",
        headers=_h(token),
        json={
            "label": "k",
            "api_key": "ABCDEFGHsecret",
            "api_secret": "seeeeeecret",
        },
    )
    created = client.post(
        "/v1/strategies",
        headers=_h(token),
        json={
            "account_id": account_id,
            "name": "live-s",
            "symbol": "BTCUSDT",
            "timeframe": "1m",
            "status": "draft",
        },
    )
    sid = created.json()["id"]
    patched = client.patch(
        f"/v1/strategies/{sid}",
        headers=_h(token),
        json={"status": "active"},
    )
    assert patched.status_code == 200, patched.text
    orders = ledger.list_orders(account_id=account_id)
    assert orders and orders[0]["status"] == "filled"


def test_live_rejects_when_notional_exceeds_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "true")
    monkeypatch.setenv("PHASE2_GATES_ACK", "true")
    monkeypatch.setenv("LIVE_NAV_QUOTE", "100000")
    monkeypatch.setenv("LIVE_MAX_NAV_PCT", "5")
    monkeypatch.setenv("LIVE_VENUE_MODE", "binance_mainnet")

    # Estimate price from market fixture may be ~100 default; force huge qty via
    # max_position_size still capped by BASELINE — instead call adapter directly.
    from gateway.trading.paper_adapter import VenueAdapterError, submit_and_fill

    acct = account_store.create_account(
        name="live",
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
            quantity=100.0,  # 100 * ~fixture price >> 5000
            risk_check_id=str(uuid4()),
            trace_id=str(uuid4()),
        )
    assert exc.value.code == "live_notional_exceeds_cap"
