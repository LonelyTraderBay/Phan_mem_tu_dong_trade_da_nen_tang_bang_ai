"""009 PROD-LIVE ≤5% NAV envelope — fail-closed; no mainnet submit."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway import (
    account_store,
    alerts_store,
    auth_store,
    kill_switch_store,
    portfolio_store,
    risk_guard,
    strategy_store,
)
from gateway.app import app
from gateway.trading import ledger
from gateway.trading.live_capital import clamp_max_nav_pct, load_policy

client = TestClient(app)
DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
    risk_guard.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    portfolio_store.clear()
    ledger.clear()
    for key in (
        "LIVE_TRADING_ENABLED",
        "PHASE2_GATES_ACK",
        "LIVE_NAV_QUOTE",
        "LIVE_MAX_NAV_PCT",
    ):
        monkeypatch.delenv(key, raising=False)
    yield
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
    risk_guard.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    portfolio_store.clear()
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


def test_clamp_never_above_5_pct() -> None:
    assert clamp_max_nav_pct(10.0) == 5.0
    assert clamp_max_nav_pct(5.0) == 5.0
    assert clamp_max_nav_pct(1.0) == 1.0


def test_policy_default_disabled() -> None:
    p = load_policy()
    assert p.live_trading_enabled is False
    assert p.phase2_gates_ack is False
    assert p.max_nav_pct == 5.0


def test_live_account_rejected_when_disabled() -> None:
    token = _login()
    acct = client.post(
        "/v1/accounts",
        headers=_h(token),
        json={
            "name": "live-acct",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": False,
        },
    )
    assert acct.status_code == 201
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
    assert patched.status_code == 403
    assert patched.json()["code"] == "live_trading_disabled"
    assert ledger.list_orders(account_id=account_id) == []


def test_live_account_rejected_when_venue_mode_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Flags+NAV set but LIVE_VENUE_MODE not binance_mainnet → fail-closed."""
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "true")
    monkeypatch.setenv("PHASE2_GATES_ACK", "true")
    monkeypatch.setenv("LIVE_NAV_QUOTE", "100000")
    monkeypatch.setenv("LIVE_MAX_NAV_PCT", "5")
    monkeypatch.delenv("LIVE_VENUE_MODE", raising=False)

    token = _login()
    acct = client.post(
        "/v1/accounts",
        headers=_h(token),
        json={
            "name": "live-acct",
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
    assert patched.status_code == 403
    assert patched.json()["code"] == "live_venue_mode_disabled"
    assert ledger.list_orders(account_id=account_id) == []


def test_testnet_account_still_works() -> None:
    token = _login()
    acct = client.post(
        "/v1/accounts",
        headers=_h(token),
        json={
            "name": "tn",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
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
            "name": "s",
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
    assert patched.status_code == 200
    assert ledger.list_orders(account_id=account_id)
