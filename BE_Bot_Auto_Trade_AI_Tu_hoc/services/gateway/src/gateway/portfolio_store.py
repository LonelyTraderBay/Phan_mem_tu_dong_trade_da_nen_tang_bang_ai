"""In-memory paper portfolio / trade-report read models (not a live broker)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

# Paper fixtures — empty by default; seed helpers exist for tests.
_positions: list[dict[str, Any]] = []
_trades: list[dict[str, Any]] = []


def clear() -> None:
    _positions.clear()
    _trades.clear()


def _parse_dt(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def seed_position(
    *,
    account_id: str,
    symbol: str = "BTCUSDT",
    side: str = "long",
    quantity: float = 0.1,
    entry_price: float = 50000.0,
    open_only: bool = True,
    strategy_id: str | None = None,
) -> dict[str, Any]:
    row = {
        "id": str(uuid4()),
        "account_id": account_id,
        "strategy_id": strategy_id,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "entry_price": entry_price,
        "mark_price": entry_price,
        "unrealized_pnl": 0.0,
        "leverage": 1.0,
        "opened_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "_open": open_only,
    }
    _positions.append(row)
    return {k: v for k, v in row.items() if not k.startswith("_")}


def seed_trade(
    *,
    account_id: str,
    symbol: str = "BTCUSDT",
    side: str = "buy",
    quantity: float = 0.1,
    price: float = 50000.0,
    strategy_id: str | None = None,
    executed_at: datetime | None = None,
) -> dict[str, Any]:
    when = executed_at or datetime.now(timezone.utc)
    row = {
        "trade_id": str(uuid4()),
        "account_id": account_id,
        "strategy_id": strategy_id,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "fee": 0.0,
        "fee_currency": "USDT",
        "realized_pnl": 0.0,
        "executed_at": when.isoformat().replace("+00:00", "Z"),
    }
    _trades.append(row)
    return dict(row)


def list_positions(
    *,
    account_id: str,
    symbol: str | None = None,
    open_only: bool = True,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _positions:
        if row["account_id"] != account_id:
            continue
        if symbol is not None and row["symbol"] != symbol:
            continue
        if open_only and not row.get("_open", True):
            continue
        out.append({k: v for k, v in row.items() if not k.startswith("_")})
    return out


def get_pnl_summary(
    *,
    account_id: str,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> dict[str, Any]:
    """Server-side stub PnL — FE must not invent these numbers."""
    _ = (from_time, to_time)  # accepted for OpenAPI parity; stub ignores range
    realized = 0.0
    unrealized = 0.0
    for pos in list_positions(account_id=account_id, open_only=False):
        unrealized += float(pos.get("unrealized_pnl") or 0.0)
    for trade in list_trades(account_id=account_id):
        realized += float(trade.get("realized_pnl") or 0.0)
    trade_count = len(list_trades(account_id=account_id, from_time=from_time, to_time=to_time))
    total = realized + unrealized
    return {
        "account_id": account_id,
        "currency": "USDT",
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "total_pnl": total,
        "gross_profit": max(total, 0.0),
        "gross_loss": min(total, 0.0),
        "trade_count": trade_count,
        "calculated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def list_trades(
    *,
    account_id: str,
    strategy_id: str | None = None,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _trades:
        if row["account_id"] != account_id:
            continue
        if strategy_id is not None and row.get("strategy_id") != strategy_id:
            continue
        executed = _parse_dt(row.get("executed_at"))
        if from_time is not None and executed is not None and executed < from_time:
            continue
        if to_time is not None and executed is not None and executed > to_time:
            continue
        out.append(dict(row))
        if len(out) >= limit:
            break
    return out
