"""API tests for kill-switch L1 + alerts stubs (P1-BE-07)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from gateway import alerts_store, auth_store, kill_switch_store
from gateway.app import app

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
    auth_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    yield
    auth_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()


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


def test_get_kill_switch_requires_auth() -> None:
    response = client.get("/v1/kill-switch")
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_post_kill_switch_requires_auth() -> None:
    response = client.post(
        "/v1/kill-switch",
        json={"engaged": True, "reason": "pause entries"},
    )
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_get_alerts_requires_auth() -> None:
    response = client.get("/v1/alerts", params={"account_id": str(uuid4())})
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_get_kill_switch_default_disengaged() -> None:
    token = _login_access()
    response = client.get("/v1/kill-switch", headers=_auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) >= {"engaged", "updated_at"}
    assert body["engaged"] is False
    assert body["reason"] is None
    assert body["updated_by"] is None


def test_post_kill_switch_engage_and_disengage() -> None:
    token = _login_access()
    headers = _auth_headers(token)

    engage = client.post(
        "/v1/kill-switch",
        headers=headers,
        json={"engaged": True, "reason": "L1 emergency pause"},
    )
    assert engage.status_code == 200
    engaged_body = engage.json()
    assert engaged_body["engaged"] is True
    assert engaged_body["reason"] == "L1 emergency pause"
    assert engaged_body["updated_at"]

    status = client.get("/v1/kill-switch", headers=headers)
    assert status.status_code == 200
    assert status.json()["engaged"] is True

    disengage = client.post(
        "/v1/kill-switch",
        headers=headers,
        json={"engaged": False, "reason": "resume paper entries"},
    )
    assert disengage.status_code == 200
    assert disengage.json()["engaged"] is False
    assert disengage.json()["reason"] == "resume paper entries"

    audit = kill_switch_store.list_audit()
    assert len(audit) == 2
    assert audit[0]["engaged"] is True
    assert audit[1]["engaged"] is False


def test_post_kill_switch_rejects_empty_reason() -> None:
    token = _login_access()
    response = client.post(
        "/v1/kill-switch",
        headers=_auth_headers(token),
        json={"engaged": True, "reason": ""},
    )
    assert response.status_code == 422


def test_get_alerts_empty_list_ok() -> None:
    token = _login_access()
    account_id = str(uuid4())
    response = client.get(
        "/v1/alerts",
        headers=_auth_headers(token),
        params={"account_id": account_id},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_alerts_fixture_shape_and_filters() -> None:
    token = _login_access()
    account_id = str(uuid4())
    alerts_store.seed_alert(
        account_id=account_id,
        severity="warning",
        code="DRAWDOWN",
        message="Paper drawdown warning",
        acknowledged=False,
    )
    alerts_store.seed_alert(
        account_id=account_id,
        severity="info",
        code="ACKED",
        message="Already seen",
        acknowledged=True,
    )
    alerts_store.seed_alert(
        account_id=str(uuid4()),
        severity="critical",
        code="OTHER",
        message="Other account",
    )

    response = client.get(
        "/v1/alerts",
        headers=_auth_headers(token),
        params={
            "account_id": account_id,
            "acknowledged": False,
            "severity": "warning",
            "limit": 10,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    row = body[0]
    assert set(row.keys()) >= {
        "id",
        "severity",
        "code",
        "message",
        "acknowledged",
        "created_at",
    }
    assert row["account_id"] == account_id
    assert row["severity"] == "warning"
    assert row["code"] == "DRAWDOWN"
    assert row["acknowledged"] is False


def test_invalid_token_401_on_all_three() -> None:
    headers = _auth_headers("access_not_a_real_token")
    account_id = str(uuid4())
    get_ks = client.get("/v1/kill-switch", headers=headers)
    post_ks = client.post(
        "/v1/kill-switch",
        headers=headers,
        json={"engaged": True, "reason": "x"},
    )
    get_alerts = client.get(
        "/v1/alerts",
        headers=headers,
        params={"account_id": account_id},
    )
    for response in (get_ks, post_ks, get_alerts):
        assert response.status_code == 401
        _assert_error_shape(response.json())
