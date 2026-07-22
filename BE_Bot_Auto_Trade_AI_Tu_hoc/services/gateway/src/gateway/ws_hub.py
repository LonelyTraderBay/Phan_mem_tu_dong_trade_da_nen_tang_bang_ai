"""In-memory Gateway WebSocket hub for paper realtime channels."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import WebSocket

PAPER_CHANNELS = frozenset(
    {
        "market.candles",
        "trading.orders",
        "trading.positions",
        "risk.kill_switch",
        "ops.alerts",
    }
)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class WsConnection:
    def __init__(self, websocket: WebSocket, subject: str) -> None:
        self.websocket = websocket
        self.subject = subject
        self.channels: set[str] = set()
        self.seq = 0
        self.buffer: list[dict[str, Any]] = []

    def next_seq(self) -> int:
        self.seq += 1
        return self.seq

    async def send_envelope(
        self,
        *,
        type_: str,
        channel: str | None = None,
        payload: dict[str, Any] | None = None,
        stale: bool = False,
        trace_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        frame: dict[str, Any] = {
            "type": type_,
            "seq": self.next_seq(),
            "produced_at_utc": _utcnow_iso(),
            "stale": stale,
            "trace_id": trace_id,
        }
        if channel is not None:
            frame["channel"] = channel
        if payload is not None:
            frame["payload"] = payload
        if extra:
            frame.update(extra)
        self.buffer.append(frame)
        if len(self.buffer) > 200:
            self.buffer = self.buffer[-200:]
        await self.websocket.send_json(frame)


class WsHub:
    def __init__(self) -> None:
        self._connections: set[WsConnection] = set()
        self._lock = asyncio.Lock()

    def clear(self) -> None:
        self._connections.clear()

    async def connect(self, conn: WsConnection) -> None:
        async with self._lock:
            self._connections.add(conn)

    async def disconnect(self, conn: WsConnection) -> None:
        async with self._lock:
            self._connections.discard(conn)

    async def broadcast(
        self,
        *,
        channel: str,
        type_: str,
        payload: dict[str, Any],
        trace_id: str | None = None,
        stale: bool = False,
    ) -> None:
        if channel not in PAPER_CHANNELS:
            return
        async with self._lock:
            targets = [c for c in self._connections if channel in c.channels]
        for conn in targets:
            try:
                await conn.send_envelope(
                    type_=type_,
                    channel=channel,
                    payload=payload,
                    stale=stale,
                    trace_id=trace_id,
                )
            except Exception:
                # Drop broken sockets; cleanup on next recv loop.
                pass


hub = WsHub()


def clear() -> None:
    hub.clear()


async def publish(
    channel: str,
    type_: str,
    payload: dict[str, Any],
    *,
    trace_id: str | None = None,
) -> None:
    await hub.broadcast(
        channel=channel,
        type_=type_,
        payload=payload,
        trace_id=trace_id or str(uuid4()),
    )


def publish_sync(
    channel: str,
    type_: str,
    payload: dict[str, Any],
    *,
    trace_id: str | None = None,
) -> None:
    """Broadcast from sync routes (threadpool-safe via anyio)."""

    async def _go() -> None:
        await publish(channel, type_, payload, trace_id=trace_id)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            from anyio.from_thread import run as anyio_run

            anyio_run(_go)
        except RuntimeError:
            asyncio.run(_go())
        return
    loop.create_task(_go())
