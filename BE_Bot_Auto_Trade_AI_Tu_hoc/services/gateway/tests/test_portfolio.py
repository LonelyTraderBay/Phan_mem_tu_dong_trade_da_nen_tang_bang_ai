"""API tests for positions / PnL / trade-report stubs (P1-BE-06)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from gateway import auth_store, portfolio_store
from gateway.app import app

client = TestClient(app)

DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
    auth_store.clear()
    portfolio_store.clear()
    yield
    auth_store.clear()
    portfolio_store.clear()


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


def test_get_positions_requires_auth() -> None:
    response = client.get("/v1/positions", params={"account_id": str(uuid4())})
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_get_pnl_summary_requires_auth() -> None:
    response = client.get("/v1/pnl/summary", params={"account_id": str(uuid4())})
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_get_reports_trades_requires_auth() -> None:
    response = client.get("/v1/reports/trades", params={"account_id": str(uuid4())})
    assert response.status_code == 401
    _assert_error_shape(response.json())


def test_get_positions_empty_list_ok() -> None:
    token = _login_access()
    account_id = str(uuid4())
    response = client.get(
        "/v1/positions",
        headers=_auth_headers(token),
        params={"account_id": account_id},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_positions_fixture_shape() -> None:
    token = _login_access()
    account_id = str(uuid4())
    portfolio_store.seed_position(account_id=account_id, symbol="ETHUSDT", side="short")

    response = client.get(
        "/v1/positions",
        headers=_auth_headers(token),
        params={"account_id": account_id, "symbol": "ETHUSDT", "open_only": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    row = body[0]
    assert set(row.keys()) >= {
        "id",
        "account_id",
        "symbol",
        "side",
        "quantity",
        "entry_price",
        "opened_at",
    }
    assert row["account_id"] == account_id
    assert row["symbol"] == "ETHUSDT"
    assert row["side"] == "short"
    assert row["quantity"] >= 0
    assert row["entry_price"] >= 0


def test_get_pnl_summary_server_stub() -> None:
    token = _login_access()
    account_id = str(uuid4())
    response = client.get(
        "/v1/pnl/summary",
        headers=_auth_headers(token),
        params={"account_id": account_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) >= {
        "account_id",
        "currency",
        "realized_pnl",
        "unrealized_pnl",
        "total_pnl",
        "calculated_at",
    }
    assert body["account_id"] == account_id
    assert isinstance(body["realized_pnl"], (int, float))
    assert isinstance(body["unrealized_pnl"], (int, float))
    assert isinstance(body["total_pnl"], (int, float))
    assert body["total_pnl"] == body["realized_pnl"] + body["unrealized_pnl"]


def test_get_reports_trades_empty_list_ok() -> None:
    token = _login_access()
    account_id = str(uuid4())
    response = client.get(
        "/v1/reports/trades",
        headers=_auth_headers(token),
        params={"account_id": account_id},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_reports_trades_fixture_shape() -> None:
    token = _login_access()
    account_id = str(uuid4())
    portfolio_store.seed_trade(account_id=account_id, symbol="BTCUSDT", side="sell")

    response = client.get(
        "/v1/reports/trades",
        headers=_auth_headers(token),
        params={"account_id": account_id, "limit": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    row = body[0]
    assert set(row.keys()) >= {
        "trade_id",
        "account_id",
        "symbol",
        "side",
        "quantity",
        "price",
        "executed_at",
    }
    assert row["account_id"] == account_id
    assert row["side"] == "sell"
    assert row["quantity"] >= 0
    assert row["price"] >= 0


def test_invalid_token_401_on_all_three() -> None:
    account_id = str(uuid4())
    headers = _auth_headers("access_not_a_real_token")
    for path in ("/v1/positions", "/v1/pnl/summary", "/v1/reports/trades"):
        response = client.get(path, headers=headers, params={"account_id": account_id})
        assert response.status_code == 401
        _assert_error_shape(response.json())
