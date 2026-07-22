# RFC-0003: Paper WebSocket realtime (ticket + locked channels)

| | |
|---|---|
| **Status** | Approved (Owner active `PAPER-WS-REALTIME` 2026-07-22) |
| **Author** | AI (Owner-directed) |
| **Date** | 2026-07-22 |
| **Approver (Owner)** | Owner — Active PAPER-WS-REALTIME |

## Summary

Lock Gateway paper WS: REST `postWsTicket`, connect `GET /ws?ticket=…`, envelope framing with `seq`, and In-MVP paper channels. FE talks only to Gateway WS.

## Motivation

`packages/contracts/ws/ws-protocol.md` required OpenAPI ticket fields and forbade FE hard-coding stub channel names without RFC. Assignment `PAPER-WS-REALTIME` needs a contract-first paper realtime path.

## Contract diff

- `packages/contracts/VERSION`: 0.2.0 → 0.3.0
- OpenAPI: `POST /v1/ws/ticket` (`postWsTicket`, `x-mvp: true`)
- `ws-protocol.md`: lock paper channel names (below)
- Align examples to locked names
- Events/RBAC: unchanged

### Locked paper channels (In-MVP)

| Channel | Purpose |
|---|---|
| `market.candles` | Candle / last-price style updates (paper) |
| `trading.orders` | Order lifecycle patches |
| `trading.positions` | Position patches |
| `risk.kill_switch` | Kill-switch L1–L4 state |
| `ops.alerts` | Operator alerts |

Out of paper MVP WS (still listed as future): `ops.approvals`, `jobs.backtest`.

## Phase

Phase 1 paper/dev. Not Event Bus to FE. Not live capital.

## Change class

- [x] **Additive public**
- [ ] **Breaking**
- [ ] **Docs-only**

## Security / safety

- Ticket short-lived, bound to session; single-use or TTL consume
- No secrets in WS payloads
- Stale: client marks silence; does not invent market data

## Rollout

1. Land OpenAPI + ws-protocol + VERSION  
2. BE ticket + `/ws` hub + broadcasts from kill-switch / paper path / alerts  
3. FE ticket + connect + stale UX  
4. Tests with TestClient websocket  
