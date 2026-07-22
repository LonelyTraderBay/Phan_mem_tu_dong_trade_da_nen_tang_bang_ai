"""Paper stubs: getStrategies / postStrategies / patchStrategy.

Activate (status→active) runs internal paper path: credentials → risk → OMS → ledger.
"""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from gateway import account_store, auth_store, risk_guard, strategy_store
from gateway.deps import require_auth
from gateway.errors import ErrorDetail, error_response
from gateway.trading import strategy_runner

router = APIRouter(prefix="/strategies", tags=["Strategies"])

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


class Strategy(BaseModel):
    id: str
    account_id: str
    name: str
    symbol: str
    timeframe: str
    status: StrategyStatus
    created_at: str
    updated_at: str | None = None
    max_position_size: float | None = None
    stop_loss_percent: float | None = None


@router.get("", response_model=list[Strategy])
def list_strategies(
    _session: Annotated[auth_store.Session, Depends(require_auth)],
    account_id: Annotated[UUID | None, Query()] = None,
    status: Annotated[StrategyStatus | None, Query()] = None,
):
    rows = strategy_store.list_strategies(
        account_id=str(account_id) if account_id is not None else None,
        status=status,
    )
    return [Strategy(**row) for row in rows]


@router.post("", status_code=201, response_model=Strategy)
def create_strategy(
    body: StrategyCreate,
    _session: Annotated[auth_store.Session, Depends(require_auth)],
):
    account_id = str(body.account_id)
    if account_store.get_account(account_id) is None:
        return error_response(
            404,
            code="not_found",
            message="Account not found",
            details=[ErrorDetail(field="account_id", reason="unknown_account")],
        )
    created = strategy_store.create_strategy(
        account_id=account_id,
        name=body.name,
        symbol=body.symbol,
        timeframe=body.timeframe,
        status=body.status if body.status is not None else "draft",
        max_position_size=body.max_position_size,
        stop_loss_percent=body.stop_loss_percent,
    )
    return Strategy(**created)


@router.patch("/{strategy_id}", response_model=Strategy)
def patch_strategy(
    strategy_id: UUID,
    body: StrategyPatch,
    _session: Annotated[auth_store.Session, Depends(require_auth)],
):
    fields_set = body.model_fields_set
    if not fields_set:
        return error_response(
            400,
            code="validation_error",
            message="At least one field is required",
            details=[ErrorDetail(field="body", reason="min_properties")],
        )

    existing = strategy_store.get_strategy(str(strategy_id))
    if existing is None:
        return error_response(
            404,
            code="not_found",
            message="Strategy not found",
            details=[ErrorDetail(field="strategy_id", reason="unknown_strategy")],
        )

    activating = "status" in fields_set and body.status == "active" and existing.status != "active"
    if activating:
        # Fail-closed risk dependency (Constitution II / P1-BE-08).
        risk_guard.ensure_entry_allowed()
        # Paper path: credentials → risk_engine (L1) → OMS → ledger (T009–T012, T018).
        result = strategy_runner.run_on_activate(existing)
        if not result.ok:
            return error_response(
                result.status_code,
                code=result.code,
                message=result.message,
                details=list(result.details),
                trace_id=result.trace_id or None,
            )

    updated = strategy_store.patch_strategy(
        str(strategy_id),
        name=body.name if "name" in fields_set else None,
        status=body.status if "status" in fields_set else None,
        timeframe=body.timeframe if "timeframe" in fields_set else None,
        max_position_size=body.max_position_size if "max_position_size" in fields_set else None,
        stop_loss_percent=body.stop_loss_percent if "stop_loss_percent" in fields_set else None,
        set_max_position_size="max_position_size" in fields_set,
        set_stop_loss_percent="stop_loss_percent" in fields_set,
    )
    if updated is None:
        return error_response(
            404,
            code="not_found",
            message="Strategy not found",
            details=[ErrorDetail(field="strategy_id", reason="unknown_strategy")],
        )
    return Strategy(**updated)
