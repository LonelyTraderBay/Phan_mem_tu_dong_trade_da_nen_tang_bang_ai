"""getKillSwitchStatus / postKillSwitch — L1–L4 paper/staging (RFC-0002)."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from gateway import alerts_store, auth_store, kill_switch_store
from gateway.deps import require_auth
from gateway.errors import ErrorDetail, error_response
from gateway.trading import ledger
from gateway.ws_hub import publish_sync

router = APIRouter(tags=["KillSwitch"])

KillLevel = Literal["L1", "L2", "L3", "L4"]


class KillSwitchRequest(BaseModel):
    engaged: bool
    reason: str = Field(min_length=1, max_length=500)
    level: KillLevel | None = None
    confirmed: bool | None = None


class KillSwitchStatus(BaseModel):
    engaged: bool
    level: KillLevel | None = None
    reason: str | None = None
    updated_at: str
    updated_by: str | None = None
    trace_id: str | None = None


def _apply_level_side_effects(level: KillLevel, *, trace_id: str) -> None:
    """Paper-internal only — does not claim live exchange flatten."""
    if level in ("L3", "L4"):
        ledger.cancel_open_orders(trace_id=trace_id)
    if level == "L4":
        ledger.flatten_all_positions(trace_id=trace_id)


@router.get("/kill-switch", response_model=KillSwitchStatus)
def get_kill_switch_status(
    _session: Annotated[auth_store.Session, Depends(require_auth)],
):
    return KillSwitchStatus(**kill_switch_store.get_status())


@router.post("/kill-switch", response_model=KillSwitchStatus)
def post_kill_switch(
    body: KillSwitchRequest,
    _session: Annotated[auth_store.Session, Depends(require_auth)],
):
    trace_id = str(uuid4())
    target_level: KillLevel | None = body.level

    if body.engaged:
        level: KillLevel = target_level or "L1"
        if level != "L1" and body.confirmed is not True:
            return error_response(
                400,
                code="confirmation_required",
                message=f"Kill-switch {level} requires confirmed=true",
                details=[
                    ErrorDetail(field="confirmed", reason="required_for_l2_plus"),
                ],
                trace_id=trace_id,
            )
        status = kill_switch_store.set_state(
            engaged=True,
            reason=body.reason,
            level=level,
            updated_by=None,
            trace_id=trace_id,
        )
        _apply_level_side_effects(level, trace_id=trace_id)
        alerts_store.seed_alert(
            account_id=None,
            severity="critical",
            code="KILL_SWITCH_ACTIVE" if level == "L1" else "KILL_SWITCH_L2_PLUS",
            message=f"Kill-switch {level} engaged (paper): {body.reason}",
        )
        publish_sync(
            "risk.kill_switch",
            "kill_switch.update",
            {
                "engaged": True,
                "level": level,
                "reason": body.reason,
                "updated_at": status.get("updated_at"),
            },
            trace_id=trace_id,
        )
        publish_sync(
            "ops.alerts",
            "alert.created",
            {
                "code": "KILL_SWITCH_ACTIVE" if level == "L1" else "KILL_SWITCH_L2_PLUS",
                "severity": "critical",
                "message": f"Kill-switch {level} engaged (paper)",
            },
            trace_id=trace_id,
        )
        return KillSwitchStatus(**status)

    # Disengage / clear
    current = kill_switch_store.get_status()
    current_level = current.get("level")
    if current_level and current_level != "L1" and body.confirmed is not True:
        return error_response(
            400,
            code="confirmation_required",
            message=f"Disengage from {current_level} requires confirmed=true",
            details=[
                ErrorDetail(field="confirmed", reason="required_for_l2_plus"),
            ],
            trace_id=trace_id,
        )

    status = kill_switch_store.set_state(
        engaged=False,
        reason=body.reason,
        level=None,
        updated_by=None,
        trace_id=trace_id,
    )
    publish_sync(
        "risk.kill_switch",
        "kill_switch.update",
        {
            "engaged": False,
            "level": None,
            "reason": body.reason,
            "updated_at": status.get("updated_at"),
        },
        trace_id=trace_id,
    )
    return KillSwitchStatus(**status)
