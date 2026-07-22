"""Kill-switch L1 engage/disengage paper stub."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from gateway.auth_deps import BearerUser
from gateway.store import PAPER_USER_ID, iso_now, store

router = APIRouter(prefix="/v1", tags=["KillSwitch"])


class KillSwitchRequest(BaseModel):
    engaged: bool
    reason: str = Field(min_length=1, max_length=500)


def _status() -> dict:
    return {
        "engaged": store.kill_switch_engaged,
        "reason": store.kill_switch_reason,
        "updated_at": store.kill_switch_updated_at,
        "updated_by": store.kill_switch_updated_by,
    }


@router.get("/kill-switch", operation_id="getKillSwitchStatus")
def get_kill_switch_status(_user: BearerUser) -> dict:
    return _status()


@router.post("/kill-switch", operation_id="postKillSwitch")
def post_kill_switch(_user: BearerUser, body: KillSwitchRequest) -> dict:
    now = iso_now()
    store.kill_switch_engaged = body.engaged
    store.kill_switch_reason = body.reason
    store.kill_switch_updated_at = now
    store.kill_switch_updated_by = str(PAPER_USER_ID)
    store.kill_switch_audit.append(
        {
            "engaged": body.engaged,
            "reason": body.reason,
            "updated_at": now,
            "updated_by": str(PAPER_USER_ID),
        }
    )
    return _status()
