"""/v1 router shell — mount MVP route modules here.

T004: undocumented POST /v1/orders removed (not in OpenAPI; paper entry is internal).
"""

from __future__ import annotations

from fastapi import APIRouter

from gateway.routers.accounts import router as accounts_router
from gateway.routers.alerts import router as alerts_router
from gateway.routers.auth import router as auth_router
from gateway.routers.kill_switch import router as kill_switch_router
from gateway.routers.market import router as market_router
from gateway.routers.portfolio import router as portfolio_router
from gateway.routers.reports import router as reports_router
from gateway.routers.strategies import router as strategies_router
from gateway.routers.ws_ticket import router as ws_ticket_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(accounts_router)
router.include_router(strategies_router)
router.include_router(market_router)
router.include_router(portfolio_router)
router.include_router(reports_router)
router.include_router(kill_switch_router)
router.include_router(alerts_router)
router.include_router(ws_ticket_router)
