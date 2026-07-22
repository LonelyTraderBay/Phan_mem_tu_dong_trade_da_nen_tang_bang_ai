"""FastAPI application skeleton for the API Gateway.

Business routes are stubs that return HTTP 501 until implemented.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="gateway",
    version="0.1.0",
    description=(
        "API Gateway skeleton. Business routes are not implemented yet "
        "and return HTTP 501 stubs."
    ),
)


class ErrorBody(BaseModel):
    code: str
    message: str
    trace_id: str
    details: list[dict] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/orders")
def create_order_stub() -> JSONResponse:
    """Example business stub — returns 501 until OMS wiring exists."""
    body = ErrorBody(
        code="not_implemented",
        message="POST /v1/orders is not implemented",
        trace_id=str(uuid4()),
        details=[{"route": "POST /v1/orders"}],
    )
    return JSONResponse(status_code=501, content=body.model_dump())
