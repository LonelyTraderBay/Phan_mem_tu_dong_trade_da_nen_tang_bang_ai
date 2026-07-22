"""In-memory paper alerts list (not a notification pipeline)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_alerts: list[dict[str, Any]] = []


def clear() -> None:
    _alerts.clear()


def seed_alert(
    *,
    account_id: str | None = None,
    severity: str = "info",
    code: str = "PAPER_STUB",
    message: str = "Paper alert",
    acknowledged: bool = False,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    row = {
        "id": str(uuid4()),
        "account_id": account_id,
        "severity": severity,
        "code": code,
        "message": message,
        "acknowledged": acknowledged,
        "created_at": now,
        "acknowledged_at": now if acknowledged else None,
    }
    _alerts.append(row)
    return dict(row)


def list_alerts(
    *,
    account_id: str,
    acknowledged: bool | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _alerts:
        # Include account-scoped and global (None) alerts.
        if row.get("account_id") not in (account_id, None):
            continue
        if acknowledged is not None and row["acknowledged"] is not acknowledged:
            continue
        if severity is not None and row["severity"] != severity:
            continue
        out.append(dict(row))
        if len(out) >= limit:
            break
    return out
