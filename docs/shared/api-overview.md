# API overview

Source of truth: `packages/contracts/` (OpenAPI, events, WS, RBAC).

## Three surfaces

| Surface | Who uses | Where defined |
|---|---|---|
| **REST** `/v1/...` | FE ↔ Gateway | `packages/contracts/openapi/openapi.yaml` |
| **WebSocket** | FE ↔ Gateway only | `packages/contracts/ws/` |
| **Events** (Kafka/Redpanda) | BE internal | `packages/contracts/events/*.schema.json` |

**Hard rule:** Frontend never connects to Event Bus, Postgres, or internal services — only Gateway.

## REST (Gateway)

Typical groups (mark `x-phase` in OpenAPI):

- Phase 1: auth, accounts/keys, strategies, market (REST), manual orders (+ `Idempotency-Key`), positions/P&L, kill-switch, backtest jobs, alerts/reports, health  
- Phase 2–3: approvals (SoD), models/MRM (retrain, promote)

Stub responses may be `501 Not Implemented`; request/response schemas must still exist so FE can generate clients.

## Events (BE only)

Envelope required on every subject: `trace_id`, `schema_version`, `produced_at_utc`, `producer_service`.

Subjects: `candle.closed`, `signal.generated`, `order.*`, `position.updated`, `fee.posted`, `risk.limit_breached`, `kill_switch.*`, `model.*`, `reconciliation.break_detected`.

## Sync hot path (not via bus)

Strategy → Risk → OMS is **synchronous RPC**, fail-closed (ADR-04). See blueprint Phần 02 / 03.
