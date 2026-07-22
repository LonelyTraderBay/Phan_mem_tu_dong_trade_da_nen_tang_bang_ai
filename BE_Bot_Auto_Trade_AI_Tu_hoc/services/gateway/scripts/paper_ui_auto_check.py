"""Auto-check full paper UI API path against a running Gateway."""

from __future__ import annotations

import sys

import httpx

BASE = "http://127.0.0.1:8000"
EMAIL = "operator@example.com"
PASSWORD = "paper-dev-password"

rows: list[tuple[str, bool, str]] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    rows.append((name, cond, detail))
    print(("PASS" if cond else "FAIL"), name, detail)


def main() -> int:
    try:
        c = httpx.Client(base_url=BASE, timeout=10.0)
        h = c.get("/health")
        ok(
            "gateway_health",
            h.status_code == 200 and h.json().get("status") == "ok",
            h.text[:80],
        )
    except Exception as e:
        ok("gateway_health", False, f"unreachable: {e}")
        print("\nABORT: Gateway không chạy.")
        return 1

    r = c.post("/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    ok("login", r.status_code == 200 and "access_token" in r.json(), f"{r.status_code}")
    if r.status_code != 200:
        return 1
    token = r.json()["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}

    r = c.post(
        "/v1/accounts",
        headers=hdr,
        json={
            "name": "auto-check",
            "exchange": "binance",
            "market_type": "spot",
            "testnet": True,
        },
    )
    ok("create_account", r.status_code == 201, f"{r.status_code} {r.text[:120]}")
    if r.status_code != 201:
        return 1
    aid = r.json()["id"]
    print("ACCOUNT_ID", aid)

    r = c.post(
        f"/v1/accounts/{aid}/api-keys",
        headers=hdr,
        json={
            "label": "auto",
            "api_key": "ABCDEFGHsecret",
            "api_secret": "seeeeeecret",
        },
    )
    body = r.json() if r.status_code == 201 else {}
    ok(
        "attach_api_key_masked",
        r.status_code == 201
        and bool(body.get("masked_api_key"))
        and "api_secret" not in body,
        str(body.get("masked_api_key")),
    )

    r = c.post(
        "/v1/strategies",
        headers=hdr,
        json={
            "account_id": aid,
            "name": "auto-s1",
            "symbol": "BTCUSDT",
            "timeframe": "1m",
        },
    )
    ok("create_strategy", r.status_code == 201, f"{r.status_code} {r.text[:120]}")
    if r.status_code != 201:
        return 1
    sid = r.json()["id"]
    print("STRATEGY_ID", sid)

    bad = c.post(
        "/v1/strategies",
        headers=hdr,
        json={
            "account_id": "adasd",
            "name": "x",
            "symbol": "x",
            "timeframe": "1m",
        },
    )
    ok("reject_bad_account_id", bad.status_code == 422, f"{bad.status_code}")

    r = c.patch(f"/v1/strategies/{sid}", headers=hdr, json={"status": "active"})
    ok(
        "activate_strategy",
        r.status_code == 200 and r.json().get("status") == "active",
        f"{r.status_code} {r.text[:100]}",
    )

    r = c.get("/v1/positions", headers=hdr, params={"account_id": aid})
    n_pos = len(r.json()) if r.status_code == 200 else 0
    ok("dashboard_positions", r.status_code == 200 and n_pos >= 1, f"n={n_pos}")

    r = c.get("/v1/pnl/summary", headers=hdr, params={"account_id": aid})
    ok("dashboard_pnl", r.status_code == 200, f"{r.status_code} {str(r.json())[:80]}")

    r = c.get("/v1/reports/trades", headers=hdr, params={"account_id": aid})
    n_tr = len(r.json()) if r.status_code == 200 else 0
    ok("dashboard_trades", r.status_code == 200 and n_tr >= 1, f"n={n_tr}")

    r = c.get("/v1/alerts", headers=hdr, params={"account_id": aid})
    n_al = len(r.json()) if r.status_code == 200 else -1
    ok("alerts_with_account_id", r.status_code == 200, f"{r.status_code} n={n_al}")

    r = c.get("/v1/alerts", headers=hdr)
    ok("alerts_without_account_id_422", r.status_code == 422, f"{r.status_code}")

    r = c.get("/v1/market/symbols", headers=hdr)
    ok("market_symbols", r.status_code == 200, f"{r.status_code}")

    r = c.post(
        "/v1/kill-switch",
        headers=hdr,
        json={"engaged": True, "reason": "auto-check L1"},
    )
    ok(
        "kill_switch_L1",
        r.status_code == 200 and r.json().get("engaged") is True,
        f"{r.status_code}",
    )

    r = c.get("/v1/alerts", headers=hdr, params={"account_id": aid})
    codes = {a.get("code") for a in r.json()} if r.status_code == 200 else set()
    ok(
        "alerts_after_ks",
        r.status_code == 200,
        f"codes={sorted(c for c in codes if c)}",
    )

    c.post(
        "/v1/kill-switch",
        headers=hdr,
        json={"engaged": False, "reason": "auto-check clear"},
    )

    failed = [n for n, p, _ in rows if not p]
    print("\n=== SUMMARY ===")
    print(
        f"passed={sum(1 for _, p, _ in rows if p)} "
        f"failed={len(failed)} total={len(rows)}"
    )
    print("ACCOUNT_ID_FOR_UI=", aid)
    print("STRATEGY_ID_FOR_UI=", sid)
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    print("RESULT: PAPER_UI_PATH_AUTO_CHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
