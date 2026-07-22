"""Paper stubs: getKillSwitchStatus / postKillSwitch. L1 engage/disengage only."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from gateway import alerts_store, auth_store, kill_switch_store
from gateway.deps import require_auth

router = APIRouter(tags=["KillSwitch"])


class KillSwitchRequest(BaseModel):
    engaged: bool
    reason: str = Field(min_length=1, max_length=500)


class KillSwitchStatus(BaseModel):
    engaged: bool
    reason: str | None = None
    updated_at: str
    updated_by: str | None = None


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
    status = kill_switch_store.set_engaged(
        engaged=body.engaged,
        reason=body.reason,
        updated_by=None,
    )
    if body.engaged:
        # T021: alert on engage — no secrets in message.
        alerts_store.seed_alert(
            account_id=None,
            severity="critical",
            code="KILL_SWITCH_ACTIVE",
            message=f"Kill-switch L1 engaged: {body.reason}",
        )
    return KillSwitchStatus(**status)
