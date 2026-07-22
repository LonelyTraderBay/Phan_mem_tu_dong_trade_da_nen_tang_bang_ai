"""Strategies CRUD paper stubs with fail-closed activate guard."""

from __future__ import annotations

from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from gateway.auth_deps import BearerUser
from gateway.errors import error_response
from gateway.store import iso_now, store

router = APIRouter(prefix="/v1", tags=["Strategies"])

StrategyStatus = Literal["draft", "active", "paused", "stopped"]
Timeframe = Literal["1m", "5m", "15m", "1h", "4h", "1d"]


class StrategyCreate(BaseModel):
    account_id: UUID
    name: str = Field(min_length=1, max_length=120)
    symbol: str = Field(min_length=1)
    timeframe: Timeframe
    status: StrategyStatus | None = None
    max_position_size: float | None = Field(default=None, ge=0)
    stop_loss_percent: float | None = Field(default=None, gt=0, le=100)


class StrategyPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    status: StrategyStatus | None = None
    timeframe: Timeframe | None = None
    max_position_size: float | None = Field(default=None, ge=0)
    stop_loss_percent: float | None = Field(default=None, gt=0, le=100)


def _reject_if_cannot_activate():
    """Fail-closed: never activate when kill-switch engaged or risk unavailable."""
    if store.kill_switch_engaged:
        return error_response(
            409,
            "KILL_SWITCH_ACTIVE",
            "Cannot activate strategy while kill-switch is engaged",
        )
    if not store.risk_available:
        return error_response(
            403,
            "RISK_UNAVAILABLE",
            "Cannot activate strategy while risk service is unavailable",
        )
    return None


@router.get("/strategies", operation_id="getStrategies")
def get_strategies(
    _user: BearerUser,
    account_id: UUID = Query(...),
    status: StrategyStatus | None = None,
) -> list[dict]:
    items = [
        s
        for s in store.strategies.values()
        if s["account_id"] == str(account_id)
        and (status is None or s["status"] == status)
    ]
    return items


@router.post("/strategies", status_code=201, operation_id="postStrategies")
def post_strategies(_user: BearerUser, body: StrategyCreate):
    account_id = str(body.account_id)
    if account_id not in store.accounts:
        return error_response(
            404,
            "NOT_FOUND",
            "Account not found",
            details=[{"field": "account_id", "reason": "unknown"}],
        )
    initial_status: StrategyStatus = body.status or "draft"
    if initial_status == "active":
        blocked = _reject_if_cannot_activate()
        if blocked is not None:
            return blocked
    now = iso_now()
    strategy_id = str(uuid4())
    strategy = {
        "id": strategy_id,
        "account_id": account_id,
        "name": body.name,
        "symbol": body.symbol,
        "timeframe": body.timeframe,
        "status": initial_status,
        "created_at": now,
        "updated_at": now,
    }
    if body.max_position_size is not None:
        strategy["max_position_size"] = body.max_position_size
    if body.stop_loss_percent is not None:
        strategy["stop_loss_percent"] = body.stop_loss_percent
    store.strategies[strategy_id] = strategy
    return strategy


@router.patch("/strategies/{strategy_id}", operation_id="patchStrategy")
def patch_strategy(strategy_id: str, _user: BearerUser, body: StrategyPatch):
    strategy = store.strategies.get(strategy_id)
    if strategy is None:
        return error_response(
            404,
            "NOT_FOUND",
            "Strategy not found",
            details=[{"field": "strategy_id", "reason": "unknown"}],
        )
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        return error_response(
            400,
            "VALIDATION_ERROR",
            "At least one field is required",
        )
    if patch.get("status") == "active":
        blocked = _reject_if_cannot_activate()
        if blocked is not None:
            return blocked
    strategy.update(patch)
    strategy["updated_at"] = iso_now()
    return strategy
