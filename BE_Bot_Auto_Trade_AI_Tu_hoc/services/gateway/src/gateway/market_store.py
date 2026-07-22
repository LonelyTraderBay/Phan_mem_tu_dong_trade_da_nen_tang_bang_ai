"""Paper market fixtures — mock symbols + OHLCV candles (not a live feed)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

# Fixture catalog is static paper data; always treated as non-live (stale).
MARKET_STALE = True

_FIXTURE_SYMBOLS: list[dict[str, Any]] = [
    {
        "symbol": "BTCUSDT",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "exchange": "binance",
        "market_type": "spot",
        "active": True,
        "price_precision": 2,
        "quantity_precision": 6,
    },
    {
        "symbol": "ETHUSDT",
        "base_asset": "ETH",
        "quote_asset": "USDT",
        "exchange": "binance",
        "market_type": "spot",
        "active": True,
        "price_precision": 2,
        "quantity_precision": 5,
    },
    {
        "symbol": "BTCUSDT",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "exchange": "binance",
        "market_type": "futures",
        "active": True,
        "price_precision": 1,
        "quantity_precision": 3,
    },
    {
        "symbol": "SOLUSDT",
        "base_asset": "SOL",
        "quote_asset": "USDT",
        "exchange": "okx",
        "market_type": "spot",
        "active": False,
        "price_precision": 3,
        "quantity_precision": 2,
    },
]

_INTERVAL_DELTA: dict[str, timedelta] = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}

_BASE_PRICES: dict[str, float] = {
    "BTCUSDT": 65000.0,
    "ETHUSDT": 3500.0,
    "SOLUSDT": 145.0,
}


def list_symbols(
    *,
    exchange: str | None = None,
    market_type: str | None = None,
) -> list[dict[str, Any]]:
    rows = _FIXTURE_SYMBOLS
    if exchange is not None:
        rows = [r for r in rows if r["exchange"] == exchange]
    if market_type is not None:
        rows = [r for r in rows if r["market_type"] == market_type]
    return [dict(r) for r in rows]


def known_symbol(symbol: str) -> bool:
    return any(r["symbol"] == symbol for r in _FIXTURE_SYMBOLS)


def list_candles(
    *,
    symbol: str,
    interval: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 500,
) -> list[dict[str, Any]]:
    """Return deterministic mock OHLCV for known symbols; empty if unknown."""
    if not known_symbol(symbol):
        return []

    delta = _INTERVAL_DELTA[interval]
    base = _BASE_PRICES.get(symbol, 100.0)
    capped = max(1, min(limit, 1000))

    end = end_time if end_time is not None else datetime.now(timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    start = start_time
    if start is not None and start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    # Align end to interval boundary (floor).
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    steps_from_epoch = int((end - epoch).total_seconds() // delta.total_seconds())
    cursor = epoch + delta * steps_from_epoch

    candles: list[dict[str, Any]] = []
    for i in range(capped):
        open_time = cursor - delta * (capped - 1 - i)
        if start is not None and open_time < start:
            continue
        if open_time > end:
            break
        # Simple deterministic wave around base price.
        drift = ((i % 11) - 5) * (base * 0.001)
        open_px = round(base + drift, 8)
        high_px = round(open_px * 1.002, 8)
        low_px = round(open_px * 0.998, 8)
        close_px = round(open_px + drift * 0.1, 8)
        volume = round(100.0 + (i % 7) * 12.5, 8)
        close_time = open_time + delta - timedelta(milliseconds=1)
        candles.append(
            {
                "symbol": symbol,
                "interval": interval,
                "open_time": open_time.isoformat().replace("+00:00", "Z"),
                "close_time": close_time.isoformat().replace("+00:00", "Z"),
                "open": open_px,
                "high": high_px,
                "low": low_px,
                "close": close_px,
                "volume": volume,
            }
        )
    return candles
