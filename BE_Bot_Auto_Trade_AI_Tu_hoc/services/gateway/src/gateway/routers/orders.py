"""Orders stub kept at HTTP 501 (OMS not wired)."""

from __future__ import annotations

from fastapi import APIRouter

from gateway.errors import error_response

router = APIRouter(prefix="/v1", tags=["Orders"])


@router.post("/orders")
def create_order_stub():
    return error_response(
        501,
        "NOT_IMPLEMENTED",
        "POST /v1/orders is not implemented",
        details=[{"field": "route", "reason": "POST /v1/orders"}],
    )
