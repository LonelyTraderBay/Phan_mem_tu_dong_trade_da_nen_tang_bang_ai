# WebSocket protocol (contracts)

FE connects **only** to Gateway WS. See also `docs/shared/websocket-protocol.md`.  
**RFC:** `docs/shared/rfcs/RFC-0003-paper-ws-realtime.md`

## Auth

1. `POST /v1/ws/ticket` (`postWsTicket`) with Bearer access token → `{ ticket, expires_at, ws_path }`.
2. Connect to Gateway: `{ws_base}{ws_path}?ticket=<ticket>` (default path `/ws`).
3. Ticket is short-lived; invalid/expired → close with policy error (no secrets in reason).

## Framing

Server event envelope:

```json
{
  "type": "<event-type>",
  "channel": "<channel>",
  "seq": 1,
  "trace_id": "<uuid-or-null>",
  "produced_at_utc": "<ISO-8601>",
  "stale": false,
  "payload": {}
}
```

- Server messages include monotonic `seq` (uint64) per connection.
- Client may send `{ "type": "resume", "last_seq": <n> }` after reconnect.
- If gap cannot be filled: `{ "type": "gap", "from_seq": ..., "to_seq": ... }` then snapshot.
- Client `{ "type": "subscribe", "channels": ["risk.kill_switch", ...] }`.
- Client `{ "type": "ping" }` → server `{ "type": "pong", "seq": ..., "produced_at_utc": ... }`.
- Server may emit `{ "type": "heartbeat", "seq": ..., "produced_at_utc": ... }`.

## Channels (locked for paper In-MVP — RFC-0003)

| Channel | Payload intent | Paper MVP |
|---|---|---|
| `market.candles` | OHLCV / last updates | yes |
| `trading.orders` | Order state updates | yes |
| `trading.positions` | Position / P&L patches | yes |
| `risk.kill_switch` | L1–L4 state | yes |
| `ops.alerts` | SEV alerts | yes |
| `ops.approvals` | Dual-control queue | later |
| `jobs.backtest` | Backtest progress | later |

FE MUST only subscribe to locked paper channels above until a new RFC expands the list.

## Stale

Heartbeat / silence beyond SLA → client marks channel/connection stale (UX rule). Do not invent data.

## Examples

See `examples/` for sample JSON frames (aligned to locked channel names).
