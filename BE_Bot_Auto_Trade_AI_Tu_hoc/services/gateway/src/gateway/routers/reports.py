"""Paper stub: getReportsTrades. In-memory read model; empty list OK."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from gateway import auth_store, portfolio_store
from gateway.deps import require_auth

router = APIRouter(prefix="/reports", tags=["Reports"])

TradeSide = Literal["buy", "sell"]


class TradeReport(BaseModel):
    trade_id: str
    account_id: str
    strategy_id: str | None = None
    symbol: str
    side: TradeSide
    quantity: float = Field(ge=0)
    price: float = Field(ge=0)
    fee: float | None = Field(default=None, ge=0)
    fee_currency: str | None = None
    realized_pnl: float | None = None
    executed_at: str


@router.get("/trades", response_model=list[TradeReport])
def get_reports_trades(
    _session: Annotated[auth_store.Session, Depends(require_auth)],
    account_id: Annotated[UUID, Query()],
    strategy_id: Annotated[UUID | None, Query()] = None,
    from_time: Annotated[datetime | None, Query(alias="from")] = None,
    to_time: Annotated[datetime | None, Query(alias="to")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
):
    rows = portfolio_store.list_trades(
        account_id=str(account_id),
        strategy_id=str(strategy_id) if strategy_id is not None else None,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
    )
    return [TradeReport(**row) for row in rows]
