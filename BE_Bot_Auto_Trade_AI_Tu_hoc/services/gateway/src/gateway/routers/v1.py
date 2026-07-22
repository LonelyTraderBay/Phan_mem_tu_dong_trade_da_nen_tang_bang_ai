"""/v1 router shell — mount future MVP route modules here; no business logic yet."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1")


class ErrorDetail(BaseModel):
    field: str
    reason: str


class ErrorBody(BaseModel):
    """Matches packages/contracts Error schema (code, message, trace_id, details)."""

    code: str
    message: str
    trace_id: str
    details: list[ErrorDetail] = Field(default_factory=list)


@router.post("/orders")
def create_order_stub() -> JSONResponse:
    """Example business stub — returns 501 until OMS wiring exists."""
    body = ErrorBody(
        code="not_implemented",
        message="POST /v1/orders is not implemented",
        trace_id=str(uuid4()),
        details=[ErrorDetail(field="route", reason="POST /v1/orders is not implemented")],
    )
    return JSONResponse(status_code=501, content=body.model_dump())
