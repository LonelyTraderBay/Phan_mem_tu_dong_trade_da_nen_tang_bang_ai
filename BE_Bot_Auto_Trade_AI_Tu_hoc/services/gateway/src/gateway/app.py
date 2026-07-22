"""FastAPI application — Phase 1 paper stubs for In-MVP Gateway routes."""

from __future__ import annotations

from fastapi import FastAPI

from gateway.auth_deps import AuthError, auth_error_handler
from gateway.routers import (
    accounts,
    alerts,
    auth,
    health,
    kill_switch,
    market,
    orders,
    portfolio,
    reports,
    strategies,
)

app = FastAPI(
    title="gateway",
    version="0.1.0",
    description="API Gateway paper stubs (P1-BE-PAPER-STUB). In-memory only.",
)

app.add_exception_handler(AuthError, auth_error_handler)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(strategies.router)
app.include_router(market.router)
app.include_router(portfolio.router)
app.include_router(reports.router)
app.include_router(kill_switch.router)
app.include_router(alerts.router)
app.include_router(orders.router)
