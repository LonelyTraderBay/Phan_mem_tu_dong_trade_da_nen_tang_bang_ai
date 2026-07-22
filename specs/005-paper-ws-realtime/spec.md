# Feature Specification: Paper WS Realtime

**Feature Branch**: `005-paper-ws-realtime`

**Created**: 2026-07-22

**Status**: Implemented

**Input**: Owner `Active PAPER-WS-REALTIME` — Gateway WebSocket paper realtime with contract-first ticket + locked channels; FE Gateway-only; stale UX; no Event Bus; no live capital.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated WS session (Priority: P1)

As a logged-in paper operator, I obtain a short-lived WS ticket via REST and connect to Gateway `/ws` so I receive sequenced frames on subscribed paper channels.

**Why this priority**: Auth + connect is the gate for all realtime UX.

**Independent Test**: `postWsTicket` → websocket connect with ticket → subscribe → receive heartbeat or snapshot; bad ticket rejected.

**Acceptance Scenarios**:

1. **Given** a valid access token, **When** `postWsTicket` is called, **Then** response includes `ticket`, `expires_at`, `ws_path`.
2. **Given** a valid ticket, **When** client connects to `/ws?ticket=…`, **Then** connection succeeds and can subscribe.
3. **Given** missing/invalid ticket, **When** client connects, **Then** connection is rejected/closed without leaking secrets.

---

### User Story 2 - Kill-switch and paper trading updates (Priority: P1)

As the operator, when kill-switch changes or a paper order fills, I receive WS events on `risk.kill_switch` / `trading.orders` / `trading.positions` without inventing client-side market math.

**Why this priority**: Proves realtime value on existing paper path.

**Independent Test**: Engage L1 via REST → WS subscriber receives `risk.kill_switch`; activate paper fill → `trading.orders` (and positions) frames.

**Acceptance Scenarios**:

1. **Given** subscribed to `risk.kill_switch`, **When** L1 engages, **Then** a frame with engaged/level arrives with increasing `seq`.
2. **Given** subscribed to trading channels, **When** paper fill occurs (internal mode), **Then** order/position update frames arrive.

---

### User Story 3 - Stale UX (Priority: P2)

As the operator, if the WS connection is silent beyond SLA, the UI marks realtime as stale and does not invent candles/prices.

**Why this priority**: Constitution-aligned honesty for feeds.

**Independent Test**: FE shows connected vs stale; no fabricated ticks when disconnected.

**Acceptance Scenarios**:

1. **Given** connected session with heartbeats, **When** UI is open, **Then** status shows live/connected.
2. **Given** connection dropped or silence, **When** SLA exceeded, **Then** UI shows stale and keeps last server values only.

---

### Edge Cases

- Resume with `last_seq` when buffer gap → `gap` then snapshot (minimal paper: gap + resubscribe snapshot OK).
- Subscribe to unknown channel → ignore or error frame; do not invent channel.
- Ticket reuse after consume/expiry → reject.

## Requirements *(mandatory)*

### Constitution Constraints

Contract-first (`postWsTicket` + ws-protocol); FE Gateway-only; no secrets; BE/FE lane ownership; paper only.

### Functional Requirements

- **FR-001**: MUST implement `postWsTicket` per OpenAPI 0.3.0+.
- **FR-002**: MUST serve Gateway WS at `ws_path` (default `/ws`) authenticated by ticket query.
- **FR-003**: MUST support subscribe to locked paper channels only (RFC-0003).
- **FR-004**: MUST assign monotonic `seq` per connection on server frames.
- **FR-005**: MUST broadcast kill-switch and paper order/position/alert updates to subscribers.
- **FR-006**: FE MUST obtain ticket via `postWsTicket` and MUST mark stale on silence/disconnect.
- **FR-007**: FE MUST NOT connect to Kafka/Event Bus; MUST NOT invent market data when stale.
- **FR-008**: MUST NOT implement Deferred / live capital / approvals/backtest WS in this feature.

## Success Criteria

- **SC-001**: pytest covers ticket + WS connect + kill-switch broadcast.
- **SC-002**: FE `tsc` green; operations map includes `postWsTicket`.
- **SC-003**: `validate_governance` PASS after contracts 0.3.0.
