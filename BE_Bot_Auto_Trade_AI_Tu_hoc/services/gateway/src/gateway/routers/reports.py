"""Trade reports paper stub."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query

from gateway.auth_deps import BearerUser

router = APIRouter(prefix="/v1/reports", tags=["Reports"])


@router.get("/trades", operation_id="getReportsTrades")
def get_reports_trades(
    _user: BearerUser,
    account_id: UUID = Query(...),
    strategy_id: UUID | None = None,
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[dict]:
    _ = (account_id, strategy_id, from_, to, limit)
    return []
