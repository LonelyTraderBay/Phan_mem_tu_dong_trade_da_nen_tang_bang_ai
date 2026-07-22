"""postWsTicket — short-lived Gateway WebSocket ticket."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from gateway import auth_store, ws_ticket_store
from gateway.deps import require_auth

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class WsTicketResponse(BaseModel):
    ticket: str
    expires_at: str
    ws_path: str


@router.post("/ticket", response_model=WsTicketResponse)
def post_ws_ticket(
    session: Annotated[auth_store.Session, Depends(require_auth)],
):
    issued = ws_ticket_store.issue(subject=session.email)
    return WsTicketResponse(**issued)
