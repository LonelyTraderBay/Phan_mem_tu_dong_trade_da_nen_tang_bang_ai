"""Market symbols + candles paper fixtures."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Query, Response

from gateway.auth_deps import BearerUser

router = APIRouter(prefix="/v1/market", tags=["Market"])

SYMBOLS = [
    {
        "symbol": "BTC/USDT",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "exchange": "binance",
        "market_type": "spot",
        "active": True,
        "price_precision": 2,
        "quantity_precision": 6,
    },
    {
        "symbol": "ETH/USDT",
        "base_asset": "ETH",
        "quote_asset": "USDT",
        "exchange": "binance",
        "market_type": "spot",
        "active": True,
        "price_precision": 2,
        "quantity_precision": 5,
    },
]


@router.get("/symbols", operation_id="getMarketSymbols")
def get_market_symbols(
    response: Response,
    _user: BearerUser,
    exchange: str | None = None,
    market_type: Literal["spot", "futures"] | None = None,
) -> list[dict]:
    # Paper feed is not live — mark stale for FE UX.
    response.headers["X-Data-Stale"] = "true"
    items = SYMBOLS
    if exchange:
        items = [s for s in items if s["exchange"] == exchange]
    if market_type:
        items = [s for s in items if s["market_type"] == market_type]
    return items


@router.get("/candles", operation_id="getMarketCandles")
def get_market_candles(
    response: Response,
    _user: BearerUser,
    symbol: str = Query(...),
    interval: Literal["1m", "5m", "15m", "1h", "4h", "1d"] = Query(...),
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = Query(default=500, ge=1, le=1000),
) -> list[dict]:
    response.headers["X-Data-Stale"] = "true"
    # Deterministic stub candles (server-side fixture only).
    end = end_time or datetime.now(timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    step = {
        "1m": timedelta(minutes=1),
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "1h": timedelta(hours=1),
        "4h": timedelta(hours=4),
        "1d": timedelta(days=1),
    }[interval]
    count = min(limit, 10)
    base_price = 50000.0 if symbol.startswith("BTC") else 3000.0
    candles: list[dict] = []
    for i in range(count - 1, -1, -1):
        open_time = end - step * (i + 1)
        close_time = open_time + step
        o = base_price + i
        candles.append(
            {
                "symbol": symbol,
                "interval": interval,
                "open_time": open_time.isoformat().replace("+00:00", "Z"),
                "close_time": close_time.isoformat().replace("+00:00", "Z"),
                "open": o,
                "high": o + 5,
                "low": o - 5,
                "close": o + 1,
                "volume": 1.0,
            }
        )
    if start_time is not None:
        st = start_time if start_time.tzinfo else start_time.replace(tzinfo=timezone.utc)
        candles = [
            c
            for c in candles
            if datetime.fromisoformat(c["open_time"].replace("Z", "+00:00")) >= st
        ]
    return candles
