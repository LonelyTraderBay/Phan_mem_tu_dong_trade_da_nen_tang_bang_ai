"""Wave 9 paper-day smoke (TestClient). Run from gateway service root."""
from __future__ import annotations

import os
import sys

from fastapi.testclient import TestClient

# ensure src on path when run as script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gateway.app import app  # noqa: E402
from gateway.risk_guard import set_risk_available  # noqa: E402

c = TestClient(app)
steps: list[tuple[str, bool, str]] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    steps.append((name, cond, detail))
    print(("PASS" if cond else "FAIL"), name, detail)


email = os.getenv("PAPER_AUTH_EMAIL", "operator@example.com")
password = os.getenv("PAPER_AUTH_PASSWORD", "paper-dev-password")

r = c.get("/health")
ok("health", r.status_code == 200 and r.json().get("status") == "ok", r.text)
r = c.get("/ready")
ok("ready", r.status_code == 200, r.text)

r = c.post("/v1/auth/login", json={"email": email, "password": password})
ok("login", r.status_code == 200 and "access_token" in r.json(), f"{r.status_code} {r.text[:200]}")
token = r.json().get("access_token") if r.status_code == 200 else None
h = {"Authorization": f"Bearer {token}"} if token else {}

r = c.post(
    "/v1/accounts",
    headers=h,
    json={"name": "smoke", "exchange": "binance", "market_type": "spot", "testnet": True},
)
ok("create_account", r.status_code == 201, f"{r.status_code}")
aid = r.json().get("id") if r.status_code == 201 else None

r = c.post(
    f"/v1/accounts/{aid}/api-keys",
    headers=h,
    json={"label": "k", "api_key": "ABCDEFGHsecret", "api_secret": "seeeeeecret"},
)
body = r.json() if r.status_code == 201 else {}
ok(
    "masked_key",
    r.status_code == 201
    and "api_secret" not in body
    and "ABCDEFGH" not in str(body)
    and bool(body.get("masked_api_key")),
    str(body.get("masked_api_key")),
)

set_risk_available(True)
r = c.post(
    "/v1/strategies",
    headers=h,
    json={"account_id": aid, "name": "s1", "symbol": "BTCUSDT", "timeframe": "1m"},
)
ok("create_strategy", r.status_code == 201, f"{r.status_code}")
sid = r.json().get("id") if r.status_code == 201 else None
r = c.patch(f"/v1/strategies/{sid}", headers=h, json={"status": "active"})
ok("activate_strategy", r.status_code == 200 and r.json().get("status") == "active", f"{r.status_code}")

r = c.get("/v1/market/symbols", headers=h)
ok(
    "market_symbols",
    r.status_code == 200 and r.headers.get("X-Market-Stale") == "true",
    f"{r.status_code} stale={r.headers.get('X-Market-Stale')}",
)
r = c.get("/v1/market/candles", headers=h, params={"symbol": "BTCUSDT", "interval": "1m", "limit": 5})
ok("market_candles", r.status_code == 200, f"{r.status_code}")

r = c.get("/v1/positions", headers=h, params={"account_id": aid})
ok("positions", r.status_code == 200, f"{r.status_code}")
r = c.get("/v1/pnl/summary", headers=h, params={"account_id": aid})
ok("pnl", r.status_code == 200, f"{r.status_code}")
r = c.get("/v1/reports/trades", headers=h, params={"account_id": aid})
ok("trades", r.status_code == 200, f"{r.status_code}")

r = c.post("/v1/kill-switch", headers=h, json={"engaged": True, "reason": "wave9 smoke"})
ok("kill_switch_engage", r.status_code == 200 and r.json().get("engaged") is True, f"{r.status_code}")
r = c.get("/v1/kill-switch", headers=h)
ok("kill_switch_status", r.status_code == 200 and r.json().get("engaged") is True, f"{r.status_code}")
r = c.get("/v1/alerts", headers=h, params={"account_id": aid})
ok("alerts", r.status_code == 200, f"{r.status_code} {r.text[:120]}")

set_risk_available(False)
r2 = c.post(
    "/v1/strategies",
    headers=h,
    json={"account_id": aid, "name": "s2", "symbol": "ETHUSDT", "timeframe": "1m"},
)
sid2 = r2.json().get("id") if r2.status_code == 201 else None
r = c.patch(f"/v1/strategies/{sid2}", headers=h, json={"status": "active"})
ok("fail_closed_activate", r.status_code >= 400, f"{r.status_code} {r.text[:160]}")
set_risk_available(True)

failed = [n for n, p, _ in steps if not p]
print("\nWAVE9_SMOKE", "PASS" if not failed else "FAIL", f"failed={failed}")
raise SystemExit(0 if not failed else 1)
