"""In-memory paper ledger: orders, fills, positions, trades, risk_checks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_orders: list[dict[str, Any]] = []
_fills: list[dict[str, Any]] = []
_positions: list[dict[str, Any]] = []
_trades: list[dict[str, Any]] = []
_risk_checks: list[dict[str, Any]] = []


def clear() -> None:
    """Reset ledger (tests)."""
    _orders.clear()
    _fills.clear()
    _positions.clear()
    _trades.clear()
    _risk_checks.clear()


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_dt(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def record_risk_check(
    *,
    decision: str,
    reason_code: str,
    trace_id: str,
    account_id: str | None = None,
    strategy_id: str | None = None,
) -> dict[str, Any]:
    row = {
        "risk_check_id": str(uuid4()),
        "decision": decision,
        "reason_code": reason_code,
        "trace_id": trace_id,
        "account_id": account_id,
        "strategy_id": strategy_id,
        "created_at": _utcnow_iso(),
    }
    _risk_checks.append(row)
    return dict(row)


def list_risk_checks() -> list[dict[str, Any]]:
    return [dict(r) for r in _risk_checks]


def record_order(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    status: str,
    risk_check_id: str,
    trace_id: str,
    strategy_id: str | None = None,
    venue_order_id: str | None = None,
    price: float | None = None,
) -> dict[str, Any]:
    now = _utcnow_iso()
    row = {
        "id": str(uuid4()),
        "account_id": account_id,
        "strategy_id": strategy_id,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "status": status,
        "risk_check_id": risk_check_id,
        "trace_id": trace_id,
        "venue_order_id": venue_order_id,
        "price": price,
        "created_at": now,
        "updated_at": now,
    }
    _orders.append(row)
    return dict(row)


def record_fill(
    *,
    order_id: str,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    trace_id: str,
    strategy_id: str | None = None,
) -> dict[str, Any]:
    row = {
        "fill_id": str(uuid4()),
        "order_id": order_id,
        "account_id": account_id,
        "strategy_id": strategy_id,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "trace_id": trace_id,
        "filled_at": _utcnow_iso(),
    }
    _fills.append(row)
    return dict(row)


def upsert_position_from_fill(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    strategy_id: str | None = None,
) -> dict[str, Any]:
    """Simple paper position: buy → long; sell → short (no netting for demo)."""
    position_side = "long" if side == "buy" else "short"
    for pos in _positions:
        if (
            pos["account_id"] == account_id
            and pos["symbol"] == symbol
            and pos.get("_open", True)
            and pos["side"] == position_side
        ):
            prev_qty = float(pos["quantity"])
            new_qty = prev_qty + quantity
            if new_qty <= 0:
                pos["_open"] = False
                pos["quantity"] = 0.0
            else:
                # Weighted average entry.
                prev_entry = float(pos["entry_price"])
                pos["entry_price"] = ((prev_entry * prev_qty) + (price * quantity)) / new_qty
                pos["quantity"] = new_qty
                pos["mark_price"] = price
            return {k: v for k, v in pos.items() if not k.startswith("_")}

    row = {
        "id": str(uuid4()),
        "account_id": account_id,
        "strategy_id": strategy_id,
        "symbol": symbol,
        "side": position_side,
        "quantity": quantity,
        "entry_price": price,
        "mark_price": price,
        "unrealized_pnl": 0.0,
        "leverage": 1.0,
        "opened_at": _utcnow_iso(),
        "_open": True,
    }
    _positions.append(row)
    return {k: v for k, v in row.items() if not k.startswith("_")}


def record_trade(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    strategy_id: str | None = None,
    realized_pnl: float = 0.0,
) -> dict[str, Any]:
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
        "realized_pnl": realized_pnl,
        "executed_at": _utcnow_iso(),
    }
    _trades.append(row)
    return dict(row)


def list_positions(
    *,
    account_id: str | None = None,
    symbol: str | None = None,
    open_only: bool = True,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _positions:
        if account_id is not None and row["account_id"] != account_id:
            continue
        if symbol is not None and row["symbol"] != symbol:
            continue
        if open_only and not row.get("_open", True):
            continue
        out.append({k: v for k, v in row.items() if not k.startswith("_")})
    return out


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


def list_orders(*, account_id: str | None = None) -> list[dict[str, Any]]:
    if account_id is None:
        return [dict(r) for r in _orders]
    return [dict(r) for r in _orders if r["account_id"] == account_id]


def list_fills(*, account_id: str | None = None) -> list[dict[str, Any]]:
    if account_id is None:
        return [dict(r) for r in _fills]
    return [dict(r) for r in _fills if r["account_id"] == account_id]


def cancel_open_orders(*, trace_id: str) -> int:
    """Mark non-terminal paper orders cancelled (L3). Returns count."""
    n = 0
    for order in _orders:
        if order.get("status") in ("filled", "cancelled", "rejected"):
            continue
        order["status"] = "cancelled"
        order["updated_at"] = _utcnow_iso()
        order["cancel_trace_id"] = trace_id
        n += 1
    return n


def flatten_all_positions(*, trace_id: str) -> int:
    """Close all open paper positions (L4 internal matcher — not live exchange)."""
    n = 0
    for pos in _positions:
        if not pos.get("_open", True):
            continue
        pos["_open"] = False
        pos["quantity"] = 0.0
        pos["flattened_at"] = _utcnow_iso()
        pos["flatten_trace_id"] = trace_id
        n += 1
    return n


def force_position_qty_for_tests(
    *,
    account_id: str,
    symbol: str,
    quantity: float,
) -> None:
    """Test helper: mutate open position qty to force recon mismatch."""
    for pos in _positions:
        if (
            pos["account_id"] == account_id
            and pos["symbol"] == symbol
            and pos.get("_open", True)
        ):
            pos["quantity"] = quantity
            return


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
    """Test helper — same shape as production positions."""
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
        "opened_at": _utcnow_iso(),
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
