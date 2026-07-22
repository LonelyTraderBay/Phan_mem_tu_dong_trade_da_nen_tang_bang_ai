"""003 prod-paper harden: L1–L4 kill-switch + reconciliation alerts."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from gateway import alerts_store, auth_store, kill_switch_store
from gateway.app import app
from gateway.trading import ledger, reconciliation

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset() -> None:
    auth_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    ledger.clear()
    reconciliation.clear()
    yield
    auth_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    ledger.clear()
    reconciliation.clear()


def _login() -> str:
    r = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_l1_engage_sets_level() -> None:
    token = _login()
    r = client.post(
        "/v1/kill-switch",
        headers=_h(token),
        json={"engaged": True, "reason": "L1 pause"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["engaged"] is True
    assert body["level"] == "L1"
    assert body["trace_id"]


def test_l2_without_confirm_rejected() -> None:
    token = _login()
    r = client.post(
        "/v1/kill-switch",
        headers=_h(token),
        json={"engaged": True, "reason": "escalate", "level": "L2"},
    )
    assert r.status_code == 400
    assert r.json()["code"] == "confirmation_required"
    assert kill_switch_store.get_status()["engaged"] is False


def test_l2_with_confirm_ok() -> None:
    token = _login()
    r = client.post(
        "/v1/kill-switch",
        headers=_h(token),
        json={
            "engaged": True,
            "reason": "L2 staging",
            "level": "L2",
            "confirmed": True,
        },
    )
    assert r.status_code == 200
    assert r.json()["level"] == "L2"
    codes = [a["code"] for a in alerts_store.list_alerts(account_id=str(uuid4()))]
    assert "KILL_SWITCH_L2_PLUS" in codes


def test_l4_flattens_paper_positions() -> None:
    token = _login()
    account_id = str(uuid4())
    ledger.seed_position(account_id=account_id, quantity=1.0)
    assert ledger.list_positions(account_id=account_id)
    r = client.post(
        "/v1/kill-switch",
        headers=_h(token),
        json={
            "engaged": True,
            "reason": "L4 paper flatten",
            "level": "L4",
            "confirmed": True,
        },
    )
    assert r.status_code == 200
    assert r.json()["level"] == "L4"
    assert ledger.list_positions(account_id=account_id, open_only=True) == []


def test_recon_ok_no_mismatch_alert() -> None:
    account_id = str(uuid4())
    # One buy fill + matching position qty.
    order = ledger.record_order(
        account_id=account_id,
        symbol="BTCUSDT",
        side="buy",
        quantity=0.5,
        status="filled",
        risk_check_id=str(uuid4()),
        trace_id=str(uuid4()),
    )
    ledger.record_fill(
        order_id=order["id"],
        account_id=account_id,
        symbol="BTCUSDT",
        side="buy",
        quantity=0.5,
        price=50000.0,
        trace_id=order["trace_id"],
    )
    ledger.seed_position(account_id=account_id, symbol="BTCUSDT", quantity=0.5)
    run = reconciliation.run_reconciliation(account_id=account_id)
    assert run["status"] == "ok"
    alerts = alerts_store.list_alerts(account_id=account_id)
    assert not any(a["code"] == "RECON_MISMATCH" for a in alerts)


def test_recon_mismatch_alert() -> None:
    account_id = str(uuid4())
    order = ledger.record_order(
        account_id=account_id,
        symbol="BTCUSDT",
        side="buy",
        quantity=0.5,
        status="filled",
        risk_check_id=str(uuid4()),
        trace_id=str(uuid4()),
    )
    ledger.record_fill(
        order_id=order["id"],
        account_id=account_id,
        symbol="BTCUSDT",
        side="buy",
        quantity=0.5,
        price=50000.0,
        trace_id=order["trace_id"],
    )
    ledger.seed_position(account_id=account_id, symbol="BTCUSDT", quantity=0.5)
    ledger.force_position_qty_for_tests(
        account_id=account_id, symbol="BTCUSDT", quantity=9.9
    )
    run = reconciliation.run_reconciliation(account_id=account_id)
    assert run["status"] == "mismatch"
    alerts = alerts_store.list_alerts(account_id=account_id)
    assert any(a["code"] == "RECON_MISMATCH" for a in alerts)
