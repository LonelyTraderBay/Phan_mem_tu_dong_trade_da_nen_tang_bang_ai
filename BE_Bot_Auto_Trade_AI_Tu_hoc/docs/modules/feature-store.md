# Feature Store / Engineering

**Blueprint:** Phần 03 Feature Engineering; ADR-06, ADR-07.

## Responsibility

Versioned technical features (RSI, MACD, …) with identical train/serve transforms. Optional LLM sentiment **off hot path**. Only authorized writers touch production store; writes audited.

## Phase

Data Service Phase 1–2 (thin Postgres/Timescale store); evaluate Feast Phase 3.

## Interfaces

- In: Market Data / calendar  
- Out: feature snapshots to Inference & Training; `feature_snapshot_id` on signals

## Fail-closed notes

Missing LLM sentiment → continue without it (do not block inference). Unauthorized write → reject. Store unavailable → no new signals / fail-closed entries.
