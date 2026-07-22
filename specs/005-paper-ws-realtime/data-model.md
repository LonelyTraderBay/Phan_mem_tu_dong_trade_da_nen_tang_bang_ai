# Data Model: Paper WS Realtime

## WsTicket

| Field | Notes |
|---|---|
| ticket | opaque random |
| session_id / subject | bound to auth session |
| expires_at | short TTL (~2 min) |
| consumed | bool optional |

## WsFrame

type, channel, seq, trace_id?, produced_at_utc, stale, payload

## Paper channels

`market.candles` | `trading.orders` | `trading.positions` | `risk.kill_switch` | `ops.alerts`
