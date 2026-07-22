"""005 paper WebSocket realtime — ticket + /ws + kill-switch broadcast."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway import (
    alerts_store,
    auth_store,
    kill_switch_store,
    ws_ticket_store,
)
from gateway.app import app
from gateway.trading import ledger
from gateway.ws_hub import clear as clear_hub

client = TestClient(app)
DEMO_EMAIL = auth_store.PAPER_AUTH_EMAIL
DEMO_PASSWORD = auth_store.PAPER_AUTH_PASSWORD


@pytest.fixture(autouse=True)
def _reset() -> None:
    auth_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    ws_ticket_store.clear()
    ledger.clear()
    clear_hub()
    yield
    auth_store.clear()
    kill_switch_store.clear()
    alerts_store.clear()
    ws_ticket_store.clear()
    ledger.clear()
    clear_hub()


def _login() -> str:
    r = client.post(
        "/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_post_ws_ticket_requires_auth() -> None:
    r = client.post("/v1/ws/ticket")
    assert r.status_code == 401


def test_post_ws_ticket_ok() -> None:
    token = _login()
    r = client.post(
        "/v1/ws/ticket",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) >= {"ticket", "expires_at", "ws_path"}
    assert body["ws_path"] == "/ws"
    assert len(body["ticket"]) >= 16


def test_ws_rejects_missing_ticket() -> None:
    with pytest.raises(Exception):
        with client.websocket_connect("/ws"):
            pass


def test_ws_subscribe_and_kill_switch_broadcast() -> None:
    token = _login()
    ticket_resp = client.post(
        "/v1/ws/ticket",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ticket_resp.status_code == 200
    ticket = ticket_resp.json()["ticket"]

    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
        welcome = ws.receive_json()
        assert welcome["type"] == "welcome"
        assert welcome["seq"] == 1

        ws.send_json(
            {
                "type": "subscribe",
                "channels": ["risk.kill_switch", "ops.alerts"],
            }
        )
        subscribed = ws.receive_json()
        assert subscribed["type"] == "subscribed"
        snapshot = ws.receive_json()
        assert snapshot["channel"] == "risk.kill_switch"
        assert snapshot["payload"]["engaged"] is False

        engage = client.post(
            "/v1/kill-switch",
            headers={"Authorization": f"Bearer {token}"},
            json={"engaged": True, "reason": "ws drill L1"},
        )
        assert engage.status_code == 200

        # May receive kill_switch and/or alerts; collect until kill_switch engaged.
        saw_engaged = False
        for _ in range(5):
            frame = ws.receive_json()
            if (
                frame.get("channel") == "risk.kill_switch"
                and frame.get("payload", {}).get("engaged") is True
            ):
                assert frame["payload"]["level"] == "L1"
                saw_engaged = True
                break
        assert saw_engaged


def test_ws_ping_pong() -> None:
    token = _login()
    ticket = client.post(
        "/v1/ws/ticket",
        headers={"Authorization": f"Bearer {token}"},
    ).json()["ticket"]
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
        ws.receive_json()  # welcome
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"
