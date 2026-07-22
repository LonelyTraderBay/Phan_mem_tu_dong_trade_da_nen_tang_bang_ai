"""FastAPI application skeleton for Data Service."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(
    title="data-service",
    version="0.1.0",
    description="Data Service skeleton. Health/ready only.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ok"}
