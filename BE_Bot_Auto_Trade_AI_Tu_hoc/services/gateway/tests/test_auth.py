"""API tests for paper-dev auth stubs (P1-BE-02)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway import auth_store
from gateway.app import app

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset_store() -> None:
    auth_store.clear()
    yield
    auth_store.clear()


def _assert_error_shape(payload: dict) -> None:
    assert "code" in payload
    assert "message" in payload
    assert "trace_id" in payload
    assert isinstance(payload.get("details", []), list)


def _assert_token_pair(payload: dict) -> None:
    assert set(payload.keys()) >= {
        "access_token",
        "refresh_token",
        "token_type",
        "expires_in",
    }
    assert payload["token_type"] == "Bearer"
    assert isinstance(payload["expires_in"], int) and payload["expires_in"] >= 1
    assert payload["access_token"]
    assert payload["refresh_token"]


def test_login_success() -> None:
    response = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert response.status_code == 200
    _assert_token_pair(response.json())


def test_login_fail_bad_password() -> None:
    response = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": "wrong-password"},
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_refresh_success() -> None:
    login = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    refresh_token = login.json()["refresh_token"]
    response = client.post(
        "/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    pair = response.json()
    _assert_token_pair(pair)
    assert pair["refresh_token"] != refresh_token


def test_refresh_fail_invalid_token() -> None:
    response = client.post(
        "/v1/auth/refresh",
        json={"refresh_token": "refresh_not_a_real_token"},
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_logout_success() -> None:
    login = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    access = login.json()["access_token"]
    refresh = login.json()["refresh_token"]
    response = client.post(
        "/v1/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
        json={"refresh_token": refresh},
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}
    # Refresh after logout must fail
    again = client.post("/v1/auth/refresh", json={"refresh_token": refresh})
    assert again.status_code == 401
