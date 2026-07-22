"""System health / ready routers."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/health", operation_id="getHealth")
def get_health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", operation_id="getReady")
def get_ready() -> dict[str, str]:
    return {"status": "ok"}
