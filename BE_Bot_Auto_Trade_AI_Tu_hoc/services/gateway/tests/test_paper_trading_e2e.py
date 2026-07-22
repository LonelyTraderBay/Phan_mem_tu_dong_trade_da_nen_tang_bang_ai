"""T016–T020: paper trading E2E — activate → fill; risk/kill deny → no entry."""

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

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
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


def _login_access() -> str:
    response = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_account_with_key(token: str) -> str:
    account_id = client.post(
        "/v1/accounts",
        headers=_auth_headers(token),
        json={
            "name": "Paper",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    ).json()["id"]
    key_resp = client.post(
        f"/v1/accounts/{account_id}/api-keys",
        headers=_auth_headers(token),
        json={"label": "paper", "api_key": "ABCDEFGHsecret", "api_secret": "seeeeeecret"},
    )
    assert key_resp.status_code == 201
    assert "api_secret" not in key_resp.json()
    return account_id


def _create_draft(token: str, account_id: str, symbol: str = "BTCUSDT") -> str:
    strategy = client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_id,
            "name": "Baseline",
            "symbol": symbol,
            "timeframe": "1m",
        },
    ).json()
    return strategy["id"]


def test_activate_with_credentials_creates_position_and_trade() -> None:
    token = _login_access()
    account_id = _create_account_with_key(token)
    strategy_id = _create_draft(token, account_id)
    risk_guard.set_risk_available(True)

    response = client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "active"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    positions = client.get(
        "/v1/positions",
        headers=_auth_headers(token),
        params={"account_id": account_id},
    )
    assert positions.status_code == 200
    assert len(positions.json()) >= 1
    assert positions.json()[0]["symbol"] == "BTCUSDT"

    trades = client.get(
        "/v1/reports/trades",
        headers=_auth_headers(token),
        params={"account_id": account_id},
    )
    assert trades.status_code == 200
    assert len(trades.json()) >= 1
    assert trades.json()[0]["side"] == "buy"

    checks = ledger.list_risk_checks()
    assert any(c["decision"] == "allow" and c["trace_id"] for c in checks)
    orders = ledger.list_orders(account_id=account_id)
    assert len(orders) >= 1
    assert orders[0]["risk_check_id"]
    assert orders[0]["trace_id"]


def test_activate_denied_when_risk_down_no_entry() -> None:
    token = _login_access()
    account_id = _create_account_with_key(token)
    strategy_id = _create_draft(token, account_id)
    risk_guard.set_risk_available(False)

    response = client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "active"},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "risk_unavailable"
    assert client.get("/v1/strategies", headers=_auth_headers(token)).json()[0]["status"] == "draft"
    assert ledger.list_orders(account_id=account_id) == []
    assert (
        client.get(
            "/v1/positions",
            headers=_auth_headers(token),
            params={"account_id": account_id},
        ).json()
        == []
    )


def test_activate_denied_when_kill_switch_engaged_no_entry() -> None:
    token = _login_access()
    account_id = _create_account_with_key(token)
    strategy_id = _create_draft(token, account_id)
    risk_guard.set_risk_available(True)

    engage = client.post(
        "/v1/kill-switch",
        headers=_auth_headers(token),
        json={"engaged": True, "reason": "L1 paper pause"},
    )
    assert engage.status_code == 200

    response = client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "active"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "kill_switch_engaged"
    assert "trace_id" in response.json()
    assert client.get("/v1/strategies", headers=_auth_headers(token)).json()[0]["status"] == "draft"
    assert ledger.list_orders(account_id=account_id) == []
    assert (
        client.get(
            "/v1/positions",
            headers=_auth_headers(token),
            params={"account_id": account_id},
        ).json()
        == []
    )

    alerts = client.get(
        "/v1/alerts",
        headers=_auth_headers(token),
        params={"account_id": account_id},
    ).json()
    codes = {a["code"] for a in alerts}
    assert "KILL_SWITCH_ACTIVE" in codes
    assert "RISK_REJECTED" in codes


def test_activate_without_credentials_denied() -> None:
    token = _login_access()
    account_id = client.post(
        "/v1/accounts",
        headers=_auth_headers(token),
        json={
            "name": "NoKey",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    ).json()["id"]
    strategy_id = _create_draft(token, account_id)
    risk_guard.set_risk_available(True)

    response = client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "active"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "credentials_required"
    assert client.get("/v1/strategies", headers=_auth_headers(token)).json()[0]["status"] == "draft"
