"""API tests for accounts + masked API key stubs (P1-BE-03)."""

from __future__ import annotations

import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from gateway import account_store, auth_store
from gateway.app import app

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD

SECRET_API_KEY = "sk_live_super_secret_key_ABCD"
SECRET_API_SECRET = "super-secret-exchange-password"
SECRET_PASSPHRASE = "passphrase-never-return"


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
    auth_store.clear()
    account_store.clear()
    yield
    auth_store.clear()
    account_store.clear()


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


def test_create_account_success() -> None:
    token = _login_access()
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
    body = response.json()
    assert set(body.keys()) >= {
        "id",
        "name",
        "exchange",
        "market_type",
        "testnet",
        "status",
        "created_at",
    }
    assert body["name"] == "Paper Binance"
    assert body["exchange"] == "binance"
    assert body["market_type"] == "spot"
    assert body["testnet"] is True
    assert body["status"] == "active"
    assert body["id"]


def test_register_api_key_returns_masked_only() -> None:
    token = _login_access()
    account = client.post(
        "/v1/accounts",
        headers=_auth_headers(token),
        json={
            "name": "Paper OKX",
            "exchange": "okx",
            "market_type": "futures",
        },
    ).json()

    response = client.post(
        f"/v1/accounts/{account['id']}/api-keys",
        headers=_auth_headers(token),
        json={
            "label": "primary",
            "api_key": SECRET_API_KEY,
            "api_secret": SECRET_API_SECRET,
            "passphrase": SECRET_PASSPHRASE,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert set(body.keys()) >= {
        "id",
        "account_id",
        "label",
        "masked_api_key",
        "created_at",
    }
    assert body["account_id"] == account["id"]
    assert body["label"] == "primary"
    assert body["masked_api_key"] == "****ABCD"
    assert "****" in body["masked_api_key"]

    raw = response.text
    assert SECRET_API_KEY not in raw
    assert SECRET_API_SECRET not in raw
    assert SECRET_PASSPHRASE not in raw

    dumped = json.dumps(body)
    assert "api_secret" not in dumped
    assert "passphrase" not in dumped
    assert body.get("api_key") is None
    assert "api_key" not in body or body["api_key"] != SECRET_API_KEY


def test_register_api_key_secret_not_in_response_json() -> None:
    token = _login_access()
    account_id = client.post(
        "/v1/accounts",
        headers=_auth_headers(token),
        json={"name": "A", "exchange": "binance", "market_type": "spot"},
    ).json()["id"]

    response = client.post(
        f"/v1/accounts/{account_id}/api-keys",
        headers=_auth_headers(token),
        json={
            "label": "trading",
            "api_key": SECRET_API_KEY,
            "api_secret": SECRET_API_SECRET,
        },
    )
    assert response.status_code == 201
    payload = response.json()
    for forbidden in ("api_key", "api_secret", "passphrase"):
        assert forbidden not in payload
    assert SECRET_API_KEY not in json.dumps(payload)
    assert SECRET_API_SECRET not in json.dumps(payload)


def test_accounts_unauthorized_without_token() -> None:
    response = client.post(
        "/v1/accounts",
        json={"name": "X", "exchange": "binance", "market_type": "spot"},
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_accounts_unauthorized_invalid_token() -> None:
    response = client.post(
        "/v1/accounts",
        headers=_auth_headers("access_not_a_real_token"),
        json={"name": "X", "exchange": "binance", "market_type": "spot"},
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_api_keys_unauthorized() -> None:
    response = client.post(
        f"/v1/accounts/{uuid4()}/api-keys",
        json={
            "label": "x",
            "api_key": "k",
            "api_secret": "s",
        },
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_api_keys_unknown_account_404() -> None:
    token = _login_access()
    missing = str(uuid4())
    response = client.post(
        f"/v1/accounts/{missing}/api-keys",
        headers=_auth_headers(token),
        json={
            "label": "x",
            "api_key": "k",
            "api_secret": "s",
        },
    )
    assert response.status_code == 404
    _assert_error_shape(response.json())
