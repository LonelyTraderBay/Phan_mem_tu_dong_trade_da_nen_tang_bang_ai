"""In-memory paper stub for strategies. No exchange worker / order placement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

StrategyStatus = Literal["draft", "active", "paused", "stopped"]
Timeframe = Literal["1m", "5m", "15m", "1h", "4h", "1d"]

ALLOWED_STATUSES: frozenset[str] = frozenset({"draft", "active", "paused", "stopped"})


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class StoredStrategy:
    id: str
    account_id: str
    name: str
    symbol: str
    timeframe: str
    status: str
    created_at: str
    updated_at: str | None = None
    max_position_size: float | None = None
    stop_loss_percent: float | None = None


_strategies: dict[str, StoredStrategy] = {}


def clear() -> None:
    """Reset store (tests)."""
    _strategies.clear()


def _to_dict(s: StoredStrategy) -> dict[str, object]:
    out: dict[str, object] = {
        "id": s.id,
        "account_id": s.account_id,
        "name": s.name,
        "symbol": s.symbol,
        "timeframe": s.timeframe,
        "status": s.status,
        "created_at": s.created_at,
    }
    if s.updated_at is not None:
        out["updated_at"] = s.updated_at
    if s.max_position_size is not None:
        out["max_position_size"] = s.max_position_size
    if s.stop_loss_percent is not None:
        out["stop_loss_percent"] = s.stop_loss_percent
    return out


def create_strategy(
    *,
    account_id: str,
    name: str,
    symbol: str,
    timeframe: str,
    status: str = "draft",
    max_position_size: float | None = None,
    stop_loss_percent: float | None = None,
) -> dict[str, object]:
    now = _utcnow_iso()
    strategy = StoredStrategy(
        id=str(uuid4()),
        account_id=account_id,
        name=name,
        symbol=symbol,
        timeframe=timeframe,
        status=status,
        created_at=now,
        updated_at=now,
        max_position_size=max_position_size,
        stop_loss_percent=stop_loss_percent,
    )
    _strategies[strategy.id] = strategy
    return _to_dict(strategy)


def list_strategies(
    *,
    account_id: str | None = None,
    status: str | None = None,
) -> list[dict[str, object]]:
    items = list(_strategies.values())
    if account_id is not None:
        items = [s for s in items if s.account_id == account_id]
    if status is not None:
        items = [s for s in items if s.status == status]
    return [_to_dict(s) for s in items]


def get_strategy(strategy_id: str) -> StoredStrategy | None:
    return _strategies.get(strategy_id)


def patch_strategy(
    strategy_id: str,
    *,
    name: str | None = None,
    status: str | None = None,
    timeframe: str | None = None,
    max_position_size: float | None = None,
    stop_loss_percent: float | None = None,
    set_max_position_size: bool = False,
    set_stop_loss_percent: bool = False,
) -> dict[str, object] | None:
    strategy = _strategies.get(strategy_id)
    if strategy is None:
        return None
    if name is not None:
        strategy.name = name
    if status is not None:
        strategy.status = status
    if timeframe is not None:
        strategy.timeframe = timeframe
    if set_max_position_size:
        strategy.max_position_size = max_position_size
    if set_stop_loss_percent:
        strategy.stop_loss_percent = stop_loss_percent
    strategy.updated_at = _utcnow_iso()
    return _to_dict(strategy)
