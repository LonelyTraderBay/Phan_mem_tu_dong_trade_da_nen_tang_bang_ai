"""Gateway WebSocket endpoint `/ws` — ticket auth + paper channel subscribe."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from gateway import kill_switch_store, market_store, ws_ticket_store
from gateway.ws_hub import PAPER_CHANNELS, WsConnection, hub

router = APIRouter(tags=["WebSocket"])


async def _send_kill_switch_snapshot(conn: WsConnection) -> None:
    status = kill_switch_store.get_status()
    await conn.send_envelope(
        type_="kill_switch.update",
        channel="risk.kill_switch",
        payload={
            "engaged": status.get("engaged", False),
            "level": status.get("level"),
            "reason": status.get("reason"),
            "updated_at": status.get("updated_at"),
        },
        trace_id=status.get("trace_id"),
    )


async def _send_market_snapshot(conn: WsConnection) -> None:
    symbols = market_store.list_symbols(exchange="binance", market_type="spot")
    if not symbols:
        return
    symbol = symbols[0]["symbol"]
    candles = market_store.list_candles(symbol=symbol, interval="1m", limit=1)
    if not candles:
        return
    c = candles[-1]
    await conn.send_envelope(
        type_="market.candle",
        channel="market.candles",
        payload={
            "symbol": symbol,
            "interval": "1m",
            "open": c.get("open"),
            "high": c.get("high"),
            "low": c.get("low"),
            "close": c.get("close"),
            "volume": c.get("volume"),
            "exchange_ts_utc": c.get("open_time") or c.get("close_time"),
        },
        stale=True,  # paper fixture feed — FE must not invent when disconnected
    )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, ticket: str | None = None) -> None:
    if not ticket:
        await websocket.close(code=4401)
        return
    issued = ws_ticket_store.consume(ticket)
    if issued is None:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    conn = WsConnection(websocket, subject=issued.subject)
    await hub.connect(conn)
    try:
        await conn.send_envelope(
            type_="welcome",
            payload={"subject": issued.subject, "channels": sorted(PAPER_CHANNELS)},
        )
        while True:
            raw = await websocket.receive_json()
            if not isinstance(raw, dict):
                continue
            msg_type = raw.get("type")
            if msg_type == "ping":
                await conn.send_envelope(type_="pong")
                continue
            if msg_type == "subscribe":
                channels = raw.get("channels") or []
                if not isinstance(channels, list):
                    continue
                for ch in channels:
                    if isinstance(ch, str) and ch in PAPER_CHANNELS:
                        conn.channels.add(ch)
                await conn.send_envelope(
                    type_="subscribed",
                    payload={"channels": sorted(conn.channels)},
                )
                if "risk.kill_switch" in conn.channels:
                    await _send_kill_switch_snapshot(conn)
                if "market.candles" in conn.channels:
                    await _send_market_snapshot(conn)
                continue
            if msg_type == "resume":
                last_seq = raw.get("last_seq")
                if not isinstance(last_seq, int):
                    continue
                if last_seq < conn.seq:
                    await conn.send_envelope(
                        type_="gap",
                        extra={"from_seq": last_seq + 1, "to_seq": conn.seq},
                    )
                    if "risk.kill_switch" in conn.channels:
                        await _send_kill_switch_snapshot(conn)
                continue
    except WebSocketDisconnect:
        pass
    finally:
        await hub.disconnect(conn)
