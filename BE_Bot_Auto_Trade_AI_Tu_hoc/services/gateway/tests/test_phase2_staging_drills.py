"""Phase-2 staging/paper drills — tooling evidence (not live gate Pass).

Maps to chaos C-* and game-day G-01 on the paper Gateway stack.
Human gates (pen-test, Risk Officer, capital NAV, on-call names, restore T1)
remain outside this suite.
"""

from __future__ import annotations

import time
from uuid import uuid4

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

client = TestClient(app)
DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset() -> None:
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
    risk_guard.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    portfolio_store.clear()
    ledger.clear()
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


def _account_with_keys(token: str) -> str:
    acct = client.post(
        "/v1/accounts",
        headers=_h(token),
        json={
            "name": "drill",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    )
    assert acct.status_code == 201
    account_id = acct.json()["id"]
    key = client.post(
        f"/v1/accounts/{account_id}/api-keys",
        headers=_h(token),
        json={
            "label": "drill",
            "api_key": "ABCDEFGHsecret",
            "api_secret": "seeeeeecret",
        },
    )
    assert key.status_code == 201
    return account_id


def _create_strategy(token: str, account_id: str) -> str:
    created = client.post(
        "/v1/strategies",
        headers=_h(token),
        json={
            "account_id": account_id,
            "name": "drill-strat",
            "symbol": "BTCUSDT",
            "timeframe": "1m",
            "status": "draft",
        },
    )
    assert created.status_code == 201
    return created.json()["id"]


def test_C02_risk_down_zero_new_entries() -> None:
    """C-02: Risk down → 0 new entries (fail-closed)."""
    token = _login()
    account_id = _account_with_keys(token)
    sid = _create_strategy(token, account_id)
    risk_guard.set_risk_available(False)
    before = len(ledger.list_orders(account_id=account_id))
    patched = client.patch(
        f"/v1/strategies/{sid}",
        headers=_h(token),
        json={"status": "active"},
    )
    assert patched.status_code == 503
    assert patched.json()["code"] == "risk_unavailable"
    assert len(ledger.list_orders(account_id=account_id)) == before


def test_C03_credentials_required_fail_closed() -> None:
    """C-03 (paper analogue): no credentials → 0 venue/ledger fills."""
    token = _login()
    acct = client.post(
        "/v1/accounts",
        headers=_h(token),
        json={
            "name": "no-keys",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    )
    account_id = acct.json()["id"]
    sid = _create_strategy(token, account_id)
    patched = client.patch(
        f"/v1/strategies/{sid}",
        headers=_h(token),
        json={"status": "active"},
    )
    assert patched.status_code == 403
    assert patched.json()["code"] == "credentials_required"
    assert ledger.list_orders(account_id=account_id) == []


def test_C05_stale_fixture_and_l1_blocks_entries() -> None:
    """C-05 partial: L1 engaged blocks entries; market fixture is non-live (stale)."""
    from gateway import market_store

    assert market_store.MARKET_STALE is True
    token = _login()
    account_id = _account_with_keys(token)
    sid = _create_strategy(token, account_id)
    engage = client.post(
        "/v1/kill-switch",
        headers=_h(token),
        json={"engaged": True, "reason": "C-05 stale drill L1"},
    )
    assert engage.status_code == 200
    patched = client.patch(
        f"/v1/strategies/{sid}",
        headers=_h(token),
        json={"status": "active"},
    )
    assert patched.status_code == 403
    assert patched.json()["code"] == "kill_switch_engaged"
    assert ledger.list_orders(account_id=account_id) == []


def test_C06_l2_without_confirm_rejected() -> None:
    """C-06 analogue: dangerous L2+ without confirmed → reject (SoD-style gate)."""
    token = _login()
    r = client.post(
        "/v1/kill-switch",
        headers=_h(token),
        json={"engaged": True, "reason": "bypass attempt", "level": "L2"},
    )
    assert r.status_code == 400
    assert r.json()["code"] == "confirmation_required"
    assert kill_switch_store.get_status()["engaged"] is False


def test_C04_sync_path_still_risk_checks_when_active() -> None:
    """C-04 paper: modular monolith always sync risk-check before fill (bus N/A)."""
    token = _login()
    account_id = _account_with_keys(token)
    sid = _create_strategy(token, account_id)
    risk_guard.set_risk_available(True)
    patched = client.patch(
        f"/v1/strategies/{sid}",
        headers=_h(token),
        json={"status": "active"},
    )
    assert patched.status_code == 200
    checks = ledger.list_risk_checks()
    assert any(c.get("decision") == "allow" for c in checks)
    assert ledger.list_orders(account_id=account_id)


def test_G01_l3_cancels_open_orders_under_30s() -> None:
    """G-01 paper: L3 cancels non-terminal orders; wall time ≤30s."""
    token = _login()
    account_id = str(uuid4())
    ledger.record_order(
        account_id=account_id,
        symbol="BTCUSDT",
        side="buy",
        quantity=0.01,
        status="submitted",
        risk_check_id=str(uuid4()),
        trace_id=str(uuid4()),
        venue_order_id="open-1",
    )
    t0 = time.perf_counter()
    r = client.post(
        "/v1/kill-switch",
        headers=_h(token),
        json={
            "engaged": True,
            "reason": "G-01 game-day L3",
            "level": "L3",
            "confirmed": True,
        },
    )
    elapsed = time.perf_counter() - t0
    assert r.status_code == 200
    assert r.json()["level"] == "L3"
    assert elapsed <= 30.0
    orders = ledger.list_orders(account_id=account_id)
    assert orders and orders[0]["status"] == "cancelled"


def test_C01_policy_unknown_no_blind_double_submit_documented() -> None:
    """C-01 paper stance: activate once → one order; re-activate same active is no-op path.

    Full UNKNOWN FSM against live venue is staging/human; here we assert no double
    fill when patching active→active after a successful paper fill.
    """
    token = _login()
    account_id = _account_with_keys(token)
    sid = _create_strategy(token, account_id)
    first = client.patch(
        f"/v1/strategies/{sid}",
        headers=_h(token),
        json={"status": "active"},
    )
    assert first.status_code == 200
    n1 = len(ledger.list_orders(account_id=account_id))
    second = client.patch(
        f"/v1/strategies/{sid}",
        headers=_h(token),
        json={"status": "active"},
    )
    assert second.status_code == 200
    n2 = len(ledger.list_orders(account_id=account_id))
    assert n1 == 1
    assert n2 == n1
