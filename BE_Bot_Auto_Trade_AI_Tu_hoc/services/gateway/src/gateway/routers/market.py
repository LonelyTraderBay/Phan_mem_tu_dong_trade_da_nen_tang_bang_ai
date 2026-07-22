"""Paper stubs: getMarketSymbols / getMarketCandles. Fixture data; not live."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, Field

from gateway import auth_store, market_store
from gateway.deps import require_auth

router = APIRouter(prefix="/market", tags=["Market"])

MarketType = Literal["spot", "futures"]
CandleInterval = Literal["1m", "5m", "15m", "1h", "4h", "1d"]

# OpenAPI MarketSymbol / Candle have no stale field — use response header only.
STALE_HEADER = "X-Market-Stale"


class MarketSymbol(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    exchange: str
    market_type: MarketType
    active: bool
    price_precision: int | None = Field(default=None, ge=0)
    quantity_precision: int | None = Field(default=None, ge=0)


class Candle(BaseModel):
    symbol: str
    interval: str
    open_time: str
    open: float
    high: float
    low: float
    close: float
    volume: float = Field(ge=0)
    close_time: str | None = None


def _mark_stale(response: Response) -> None:
    """Paper fixtures are never a live feed — always advertise stale."""
    if market_store.MARKET_STALE:
        response.headers[STALE_HEADER] = "true"


@router.get("/symbols", response_model=list[MarketSymbol])
def list_market_symbols(
    response: Response,
    _session: Annotated[auth_store.Session, Depends(require_auth)],
    exchange: Annotated[str | None, Query()] = None,
    market_type: Annotated[MarketType | None, Query()] = None,
):
    _mark_stale(response)
    rows = market_store.list_symbols(exchange=exchange, market_type=market_type)
    return [MarketSymbol(**row) for row in rows]


@router.get("/candles", response_model=list[Candle])
def list_market_candles(
    response: Response,
    _session: Annotated[auth_store.Session, Depends(require_auth)],
    symbol: Annotated[str, Query(min_length=1)],
    interval: Annotated[CandleInterval, Query()],
    start_time: Annotated[datetime | None, Query()] = None,
    end_time: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 500,
):
    _mark_stale(response)
    rows = market_store.list_candles(
        symbol=symbol,
        interval=interval,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )
    # Unknown symbol → empty list + stale header (no stale body field in OpenAPI).
    return [Candle(**row) for row in rows]
