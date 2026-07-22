"""FastAPI application skeleton for the API Gateway.

System probes live on the app root. MVP business routes mount under /v1.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gateway.errors import GatewayError, error_response
from gateway.routers import v1_router
from gateway.ws_endpoint import router as ws_router

app = FastAPI(
    title="gateway",
    version="0.1.0",
    description=(
        "API Gateway. Auth, accounts, strategies, market, positions/PnL, "
        "trade-report, kill-switch, alerts under /v1; paper WebSocket at /ws "
        "(ticket via postWsTicket)."
    ),
)

# Paper local UI (Next.js :3000) → Gateway :8000. Without this, browsers report
# "Failed to fetch" on login. Keep origins tight to local FE only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(ws_router)
