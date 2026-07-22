"""/v1 router shell — mount MVP route modules here."""

from __future__ import annotations

from fastapi import APIRouter

from gateway.errors import ErrorDetail, error_response
from gateway.routers.accounts import router as accounts_router
from gateway.routers.auth import router as auth_router
from gateway.routers.market import router as market_router
from gateway.routers.strategies import router as strategies_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(accounts_router)
router.include_router(strategies_router)
router.include_router(market_router)


@router.post("/orders")
def create_order_stub():
    """Example business stub — returns 501 until OMS wiring exists."""
    return error_response(
        501,
        code="not_implemented",
        message="POST /v1/orders is not implemented",
        details=[ErrorDetail(field="route", reason="POST /v1/orders is not implemented")],
    )
