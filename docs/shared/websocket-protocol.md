# WebSocket protocol (summary)

**Detail lives in** `packages/contracts/ws/ws-protocol.md` (+ examples).

## Rules

- FE connects **only** to Gateway WS (not Event Bus).
- Auth via short-lived ticket bound to JWT session.
- **Resume-from-sequence:** client sends `last_seq`; server replays or sends snapshot + gap warning.
- Stale feeds must be marked; UI shows stale, does not invent prices.
- Backpressure: slow clients may be disconnected; reconnect with jittered backoff.

## Typical channels (names finalized in contracts)

**Paper In-MVP (RFC-0003, locked):** `market.candles`, `trading.orders`, `trading.positions`, `risk.kill_switch`, `ops.alerts`.

Auth: `POST /v1/ws/ticket` (`postWsTicket`) → connect `{ws_path}?ticket=`.

Later (not paper MVP WS): approval queue, backtest job progress.
