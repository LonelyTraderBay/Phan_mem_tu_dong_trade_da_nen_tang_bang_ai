"""FastAPI application skeleton for the API Gateway.

System probes live on the app root. MVP business routes mount under /v1.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from gateway.errors import GatewayError, error_response
from gateway.routers import v1_router

app = FastAPI(
    title="gateway",
    version="0.1.0",
    description=(
        "API Gateway. Auth, accounts, strategies, market, positions/PnL, "
        "trade-report, L1 kill-switch, and alerts paper stubs under /v1; "
        "other business routes return HTTP 501 until implemented."
    ),
)


@app.exception_handler(GatewayError)
async def gateway_error_handler(_request: Request, exc: GatewayError) -> JSONResponse:
    return error_response(
        exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
        trace_id=exc.trace_id,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(v1_router)
