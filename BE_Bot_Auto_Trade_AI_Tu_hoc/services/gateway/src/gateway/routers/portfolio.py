"""Paper stubs: getPositions / getPnlSummary. Server-side PnL only; empty OK."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from gateway import auth_store, portfolio_store
from gateway.deps import require_auth

router = APIRouter(tags=["Portfolio"])

PositionSide = Literal["long", "short"]


class Position(BaseModel):
    id: str
    account_id: str
    strategy_id: str | None = None
    symbol: str
    side: PositionSide
    quantity: float = Field(ge=0)
    entry_price: float = Field(ge=0)
    mark_price: float | None = Field(default=None, ge=0)
    unrealized_pnl: float | None = None
    leverage: float | None = Field(default=None, ge=1)
    opened_at: str


class PnlSummary(BaseModel):
    account_id: str
    currency: str
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    gross_profit: float | None = None
    gross_loss: float | None = None
    trade_count: int | None = Field(default=None, ge=0)
    calculated_at: str


@router.get("/positions", response_model=list[Position])
def get_positions(
    _session: Annotated[auth_store.Session, Depends(require_auth)],
    account_id: Annotated[UUID, Query()],
    symbol: Annotated[str | None, Query()] = None,
    open_only: Annotated[bool, Query()] = True,
):
    rows = portfolio_store.list_positions(
        account_id=str(account_id),
        symbol=symbol,
        open_only=open_only,
    )
    return [Position(**row) for row in rows]


@router.get("/pnl/summary", response_model=PnlSummary)
def get_pnl_summary(
    _session: Annotated[auth_store.Session, Depends(require_auth)],
    account_id: Annotated[UUID, Query()],
    from_time: Annotated[datetime | None, Query(alias="from")] = None,
    to_time: Annotated[datetime | None, Query(alias="to")] = None,
):
    row = portfolio_store.get_pnl_summary(
        account_id=str(account_id),
        from_time=from_time,
        to_time=to_time,
    )
    return PnlSummary(**row)
