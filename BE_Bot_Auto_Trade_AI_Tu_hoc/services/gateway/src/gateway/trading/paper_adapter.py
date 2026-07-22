"""Internal paper matcher — fills buy/sell at last candle close or fallback price."""

from __future__ import annotations

from typing import Any

from gateway import market_store
from gateway.trading import ledger

DEFAULT_FILL_PRICE = 100.0
DEFAULT_INTERVAL = "1m"


def resolve_fill_price(symbol: str, interval: str = DEFAULT_INTERVAL) -> float:
    candles = market_store.list_candles(symbol=symbol, interval=interval, limit=1)
    if candles:
        return float(candles[-1]["close"])
    return DEFAULT_FILL_PRICE


def submit_and_fill(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    risk_check_id: str,
    trace_id: str,
    strategy_id: str | None = None,
    interval: str = DEFAULT_INTERVAL,
) -> dict[str, Any]:
    """Accept order, fill immediately at paper price, update ledger."""
    price = resolve_fill_price(symbol, interval=interval)
    order = ledger.record_order(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        status="filled",
        risk_check_id=risk_check_id,
        trace_id=trace_id,
        strategy_id=strategy_id,
        venue_order_id=f"paper-{trace_id[:8]}",
        price=price,
    )
    ledger.record_fill(
        order_id=order["id"],
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        trace_id=trace_id,
        strategy_id=strategy_id,
    )
    position = ledger.upsert_position_from_fill(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        strategy_id=strategy_id,
    )
    trade = ledger.record_trade(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        strategy_id=strategy_id,
    )
    return {
        "order": order,
        "position": position,
        "trade": trade,
        "fill_price": price,
    }
