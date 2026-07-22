"""P1-BE-08: fail-closed entries when risk unavailable."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway import account_store, auth_store, risk_guard, strategy_store
from gateway.app import app
from gateway.errors import GatewayError

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
    risk_guard.clear()
    yield
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
    risk_guard.clear()


def _login_access() -> str:
    response = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_draft_strategy(token: str) -> str:
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
    strategy = client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_id,
            "name": "Entry guard",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    ).json()
    return strategy["id"]


def test_ensure_entry_allowed_when_risk_available() -> None:
    risk_guard.set_risk_available(True)
    risk_guard.ensure_entry_allowed()  # must not raise
    assert risk_guard.is_risk_available() is True


def test_ensure_entry_rejects_when_risk_unavailable() -> None:
    risk_guard.set_risk_available(False)
    with pytest.raises(GatewayError) as exc_info:
        risk_guard.ensure_entry_allowed()
    err = exc_info.value
    assert err.status_code == 503
    assert err.code == "risk_unavailable"
    assert risk_guard.is_risk_available() is False


def test_patch_strategy_active_allowed_when_risk_up() -> None:
    token = _login_access()
    strategy_id = _create_draft_strategy(token)
    risk_guard.set_risk_available(True)

    response = client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "active"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_patch_strategy_active_rejected_when_risk_down() -> None:
    token = _login_access()
    strategy_id = _create_draft_strategy(token)
    risk_guard.set_risk_available(False)

    response = client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "active"},
    )
    assert response.status_code == 503
    body = response.json()
    assert body["code"] == "risk_unavailable"
    assert "trace_id" in body
    # Must not fail-open: strategy stays draft.
    listed = client.get("/v1/strategies", headers=_auth_headers(token)).json()
    assert listed[0]["status"] == "draft"


def test_patch_non_active_status_allowed_when_risk_down() -> None:
    """Pause/stop are not new entries — still allowed when risk is down."""
    token = _login_access()
    strategy_id = _create_draft_strategy(token)
    risk_guard.set_risk_available(True)
    client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "active"},
    )
    risk_guard.set_risk_available(False)

    response = client.patch(
        f"/v1/strategies/{strategy_id}",
        headers=_auth_headers(token),
        json={"status": "paused"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paused"
