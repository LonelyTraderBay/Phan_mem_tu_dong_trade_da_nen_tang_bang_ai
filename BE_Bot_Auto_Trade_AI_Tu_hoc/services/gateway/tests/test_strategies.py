"""API tests for simple strategy stubs (P1-BE-04)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from gateway import account_store, auth_store, strategy_store
from gateway.app import app

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()
    yield
    auth_store.clear()
    account_store.clear()
    strategy_store.clear()


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


def _create_account(token: str) -> str:
    response = client.post(
        "/v1/accounts",
        headers=_auth_headers(token),
        json={
            "name": "Paper Binance",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_strategy_defaults_to_draft() -> None:
    token = _login_access()
    account_id = _create_account(token)
    response = client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_id,
            "name": "EMA cross",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert set(body.keys()) >= {
        "id",
        "account_id",
        "name",
        "symbol",
        "timeframe",
        "status",
        "created_at",
    }
    assert body["account_id"] == account_id
    assert body["name"] == "EMA cross"
    assert body["symbol"] == "BTCUSDT"
    assert body["timeframe"] == "1h"
    assert body["status"] == "draft"
    assert body["id"]


def test_create_strategy_with_explicit_status() -> None:
    token = _login_access()
    account_id = _create_account(token)
    response = client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_id,
            "name": "Active bot",
            "symbol": "ETHUSDT",
            "timeframe": "15m",
            "status": "active",
            "max_position_size": 0.5,
            "stop_loss_percent": 2.5,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "active"
    assert body["max_position_size"] == 0.5
    assert body["stop_loss_percent"] == 2.5


def test_create_strategy_unknown_account_404() -> None:
    token = _login_access()
    response = client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": str(uuid4()),
            "name": "Orphan",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    )
    assert response.status_code == 404
    _assert_error_shape(response.json())


def test_list_strategies_and_filters() -> None:
    token = _login_access()
    account_a = _create_account(token)
    account_b = client.post(
        "/v1/accounts",
        headers=_auth_headers(token),
        json={"name": "B", "exchange": "okx", "market_type": "futures"},
    ).json()["id"]

    created_a = client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_a,
            "name": "A draft",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    ).json()
    client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_a,
            "name": "A active",
            "symbol": "ETHUSDT",
            "timeframe": "5m",
            "status": "active",
        },
    )
    client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_b,
            "name": "B draft",
            "symbol": "SOLUSDT",
            "timeframe": "1d",
        },
    )

    all_resp = client.get("/v1/strategies", headers=_auth_headers(token))
    assert all_resp.status_code == 200
    assert len(all_resp.json()) == 3

    by_account = client.get(
        "/v1/strategies",
        headers=_auth_headers(token),
        params={"account_id": account_a},
    )
    assert by_account.status_code == 200
    assert len(by_account.json()) == 2
    assert all(s["account_id"] == account_a for s in by_account.json())

    by_status = client.get(
        "/v1/strategies",
        headers=_auth_headers(token),
        params={"status": "draft"},
    )
    assert by_status.status_code == 200
    assert len(by_status.json()) == 2
    assert all(s["status"] == "draft" for s in by_status.json())

    both = client.get(
        "/v1/strategies",
        headers=_auth_headers(token),
        params={"account_id": account_a, "status": "draft"},
    )
    assert both.status_code == 200
    assert len(both.json()) == 1
    assert both.json()[0]["id"] == created_a["id"]


def test_patch_strategy_status_and_name() -> None:
    token = _login_access()
    account_id = _create_account(token)
    strategy = client.post(
        "/v1/strategies",
        headers=_auth_headers(token),
        json={
            "account_id": account_id,
            "name": "Before",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    ).json()

    # Allow-all among draft|active|paused|stopped for stub.
    for new_status in ("active", "paused", "stopped", "draft"):
        response = client.patch(
            f"/v1/strategies/{strategy['id']}",
            headers=_auth_headers(token),
            json={"status": new_status},
        )
        assert response.status_code == 200
        assert response.json()["status"] == new_status

    renamed = client.patch(
        f"/v1/strategies/{strategy['id']}",
        headers=_auth_headers(token),
        json={"name": "After", "timeframe": "4h"},
    )
    assert renamed.status_code == 200
    body = renamed.json()
    assert body["name"] == "After"
    assert body["timeframe"] == "4h"
    assert body["updated_at"]


def test_patch_strategy_unknown_404() -> None:
    token = _login_access()
    response = client.patch(
        f"/v1/strategies/{uuid4()}",
        headers=_auth_headers(token),
        json={"status": "paused"},
    )
    assert response.status_code == 404
    _assert_error_shape(response.json())


def test_strategies_unauthorized_without_token() -> None:
    response = client.get("/v1/strategies")
    assert response.status_code == 401
    _assert_error_shape(response.json())

    response = client.post(
        "/v1/strategies",
        json={
            "account_id": str(uuid4()),
            "name": "X",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())

    response = client.patch(
        f"/v1/strategies/{uuid4()}",
        json={"status": "active"},
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_strategies_unauthorized_invalid_token() -> None:
    response = client.get(
        "/v1/strategies",
        headers=_auth_headers("access_not_a_real_token"),
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())
