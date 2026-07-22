# WebSocket protocol (contracts)

FE connects **only** to Gateway WS. See also `docs/shared/websocket-protocol.md`.

## Auth

1. Obtain short-lived WS ticket via REST (authenticated JWT session).
2. Connect with ticket in query or first message (exact field names in OpenAPI when added).

## Framing

- Server messages include monotonic `seq` (uint64) per connection/channel namespace.
- Client may send `{ "type": "resume", "last_seq": <n> }` after reconnect.
- If gap cannot be filled: `{ "type": "gap", "from_seq": ..., "to_seq": ... }` then snapshot.

## Channels (stub names — lock via RFC before FE hard-codes)

| Channel | Payload intent |
|---|---|
| `market.candles` | OHLCV updates |
| `trading.orders` | Order state machine updates |
| `trading.positions` | Position / P&L patches |
| `risk.kill_switch` | L1–L4 state |
| `ops.alerts` | SEV alerts |
| `ops.approvals` | Dual-control queue |
| `jobs.backtest` | Backtest progress |

## Stale

Heartbeat / silence beyond SLA → client marks channel stale (UX rule). Do not invent data.

## Examples

See `examples/` for sample JSON frames (expand as contract matures).
