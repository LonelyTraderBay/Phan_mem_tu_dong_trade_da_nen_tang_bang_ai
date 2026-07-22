"""Portfolio positions + PnL summary (server-side numbers only)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query

from gateway.auth_deps import BearerUser
from gateway.store import iso_now

router = APIRouter(prefix="/v1", tags=["Portfolio"])


@router.get("/positions", operation_id="getPositions")
def get_positions(
    _user: BearerUser,
    account_id: UUID = Query(...),
    symbol: str | None = None,
    open_only: bool = Query(default=True),
) -> list[dict]:
    # Empty paper ledger is schema-valid.
    _ = (account_id, symbol, open_only)
    return []


@router.get("/pnl/summary", operation_id="getPnlSummary")
def get_pnl_summary(
    _user: BearerUser,
    account_id: UUID = Query(...),
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = None,
) -> dict:
    _ = (from_, to)
    return {
        "account_id": str(account_id),
        "currency": "USDT",
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "total_pnl": 0.0,
        "gross_profit": 0.0,
        "gross_loss": 0.0,
        "trade_count": 0,
        "calculated_at": iso_now(),
    }
