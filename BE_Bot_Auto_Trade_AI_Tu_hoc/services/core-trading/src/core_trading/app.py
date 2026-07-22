"""FastAPI application skeleton for Core Trading.

Health/ready only — business modules live under subpackages as stubs.
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(
    title="core-trading",
    version="0.1.0",
    description="Core Trading Service skeleton. No business routes yet.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ok"}
