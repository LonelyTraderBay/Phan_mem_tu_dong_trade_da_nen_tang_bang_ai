"""Paper stub: getAlerts. Empty list OK; seed helpers for tests."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from gateway import alerts_store, auth_store
from gateway.deps import require_auth

router = APIRouter(tags=["Alerts"])

AlertSeverity = Literal["info", "warning", "critical"]


class Alert(BaseModel):
    id: str
    account_id: str | None = None
    severity: AlertSeverity
    code: str
    message: str
    acknowledged: bool
    created_at: str
    acknowledged_at: str | None = None


@router.get("/alerts", response_model=list[Alert])
def get_alerts(
    _session: Annotated[auth_store.Session, Depends(require_auth)],
    account_id: Annotated[UUID, Query()],
    acknowledged: Annotated[bool | None, Query()] = None,
    severity: Annotated[AlertSeverity | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    rows = alerts_store.list_alerts(
        account_id=str(account_id),
        acknowledged=acknowledged,
        severity=severity,
        limit=limit,
    )
    return [Alert(**row) for row in rows]
