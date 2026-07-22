"""FastAPI application skeleton for the API Gateway.

System probes live on the app root. MVP business routes mount under /v1.
"""

from __future__ import annotations

from fastapi import FastAPI

from gateway.routers import v1_router

app = FastAPI(
    title="gateway",
    version="0.1.0",
    description=(
        "API Gateway. Auth paper stubs under /v1/auth; other business "
        "routes return HTTP 501 until implemented."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(v1_router)
