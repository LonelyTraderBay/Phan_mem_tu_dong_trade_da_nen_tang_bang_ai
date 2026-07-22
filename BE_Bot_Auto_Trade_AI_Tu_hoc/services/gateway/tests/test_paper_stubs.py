"""Gateway paper-stub tests: auth, masking, kill-switch, fail-closed hook."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway.app import app
from gateway.routers.accounts import mask_api_key
from gateway.store import PAPER_EMAIL, PAPER_PASSWORD, store

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_store() -> None:
    store.reset()


def _login() -> str:
    resp = client.post(
        "/v1/auth/login",
        json={"email": PAPER_EMAIL, "password": PAPER_PASSWORD},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_200() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_login_happy_path() -> None:
    response = client.post(
        "/v1/auth/login",
        json={"email": PAPER_EMAIL, "password": PAPER_PASSWORD},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] >= 1
    assert body["access_token"]
    assert body["refresh_token"]


def test_auth_login_wrong_password_returns_401_error_shape() -> None:
    response = client.post(
        "/v1/auth/login",
        json={"email": PAPER_EMAIL, "password": "WrongPass!999"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHORIZED"
    assert "message" in body
    assert "trace_id" in body


def test_auth_refresh_and_logout() -> None:
    login = client.post(
        "/v1/auth/login",
        json={"email": PAPER_EMAIL, "password": PAPER_PASSWORD},
    ).json()
    refreshed = client.post(
        "/v1/auth/refresh",
        json={"refresh_token": login["refresh_token"]},
    )
    assert refreshed.status_code == 200
    new_pair = refreshed.json()
    assert new_pair["access_token"] != login["access_token"]

    logout = client.post(
        "/v1/auth/logout",
        headers=_auth_headers(new_pair["access_token"]),
        json={"refresh_token": new_pair["refresh_token"]},
    )
    assert logout.status_code == 200
    assert logout.json() == {"success": True}


def test_mask_api_key_last_four_only() -> None:
    assert mask_api_key("abcdefghij") == "****ghij"
    token = _login()
    account = client.post(
        "/v1/accounts",
        headers=_auth_headers(token),
        json={
            "name": "paper",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    )
    assert account.status_code == 201
    account_id = account.json()["id"]
    keys = client.post(
        f"/v1/accounts/{account_id}/api-keys",
        headers=_auth_headers(token),
        json={
            "label": "primary",
            "api_key": "livekeyXYZ9abcd",
            "api_secret": "super-secret-value",
        },
    )
    assert keys.status_code == 201
    body = keys.json()
    assert body["masked_api_key"] == "****abcd"
    assert "api_secret" not in body
    assert body["masked_api_key"].count("*") >= 4
    dumped = str(body)
    assert "super-secret-value" not in dumped
    assert "livekeyXYZ9abcd" not in dumped


def test_kill_switch_l1_engage_disengage() -> None:
    token = _login()
    headers = _auth_headers(token)
    status = client.get("/v1/kill-switch", headers=headers)
    assert status.status_code == 200
    assert status.json()["engaged"] is False

    engaged = client.post(
        "/v1/kill-switch",
        headers=headers,
        json={"engaged": True, "reason": "paper drill"},
    )
    assert engaged.status_code == 200
    assert engaged.json()["engaged"] is True
    assert engaged.json()["reason"] == "paper drill"

    cleared = client.post(
        "/v1/kill-switch",
        headers=headers,
        json={"engaged": False, "reason": "resume paper"},
    )
    assert cleared.status_code == 200
    assert cleared.json()["engaged"] is False


def test_fail_closed_blocks_activate_when_kill_switch_engaged() -> None:
    token = _login()
    headers = _auth_headers(token)
    account = client.post(
        "/v1/accounts",
        headers=headers,
        json={
            "name": "paper",
            "exchange": "binance",
            "market_type": "spot",
        },
    ).json()
    strategy = client.post(
        "/v1/strategies",
        headers=headers,
        json={
            "account_id": account["id"],
            "name": "s1",
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "status": "draft",
        },
    ).json()
    client.post(
        "/v1/kill-switch",
        headers=headers,
        json={"engaged": True, "reason": "halt"},
    )
    patched = client.patch(
        f"/v1/strategies/{strategy['id']}",
        headers=headers,
        json={"status": "active"},
    )
    assert patched.status_code == 409
    assert patched.json()["code"] == "KILL_SWITCH_ACTIVE"


def test_fail_closed_blocks_activate_when_risk_unavailable() -> None:
    token = _login()
    headers = _auth_headers(token)
    account = client.post(
        "/v1/accounts",
        headers=headers,
        json={
            "name": "paper",
            "exchange": "binance",
            "market_type": "spot",
        },
    ).json()
    strategy = client.post(
        "/v1/strategies",
        headers=headers,
        json={
            "account_id": account["id"],
            "name": "s1",
            "symbol": "BTC/USDT",
            "timeframe": "1h",
        },
    ).json()
    store.risk_available = False
    patched = client.patch(
        f"/v1/strategies/{strategy['id']}",
        headers=headers,
        json={"status": "active"},
    )
    assert patched.status_code == 403
    assert patched.json()["code"] == "RISK_UNAVAILABLE"


def test_market_candles_set_stale_header() -> None:
    token = _login()
    response = client.get(
        "/v1/market/candles",
        headers=_auth_headers(token),
        params={"symbol": "BTC/USDT", "interval": "1h", "limit": 3},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Data-Stale") == "true"
    assert len(response.json()) == 3
