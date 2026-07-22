"""/v1 router shell — mount MVP route modules here."""

from __future__ import annotations

from fastapi import APIRouter

from gateway.errors import ErrorDetail, error_response
from gateway.routers.auth import router as auth_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)


@router.post("/orders")
def create_order_stub():
    """Example business stub — returns 501 until OMS wiring exists."""
    return error_response(
        501,
        code="not_implemented",
        message="POST /v1/orders is not implemented",
        details=[ErrorDetail(field="route", reason="POST /v1/orders is not implemented")],
    )
