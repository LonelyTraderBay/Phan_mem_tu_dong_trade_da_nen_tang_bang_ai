"""Alerts inbox paper stub."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query

from gateway.auth_deps import BearerUser
from gateway.store import store

router = APIRouter(prefix="/v1", tags=["Alerts"])

AlertSeverity = Literal["info", "warning", "critical"]


@router.get("/alerts", operation_id="getAlerts")
def get_alerts(
    _user: BearerUser,
    account_id: UUID = Query(...),
    acknowledged: bool | None = None,
    severity: AlertSeverity | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict]:
    items = store.alerts
    # account_id required by contract; paper fixture may be global (null account).
    filtered = []
    for alert in items:
        aid = alert.get("account_id")
        if aid is not None and aid != str(account_id):
            continue
        if acknowledged is not None and alert["acknowledged"] != acknowledged:
            continue
        if severity is not None and alert["severity"] != severity:
            continue
        filtered.append(alert)
    return filtered[:limit]
