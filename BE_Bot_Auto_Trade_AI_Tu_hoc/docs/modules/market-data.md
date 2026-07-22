# Market Data Service

**Blueprint:** Phần 03 Market Data; ADR-05.

## Responsibility

Ingest via Adapter, persist OHLCV/book to TimescaleDB, publish `candle.closed`, attach clock skew, integrate Market Calendar (session/halt/holiday).

## Phase

Data Service (with Feature Store) Phase 1.

## Interfaces

- In: Adapter streams / polls  
- Out: TimescaleDB; Event Bus `candle.closed`  
- Calendar API for Risk / Strategy

## Fail-closed notes

Dead feed for a symbol → L1 local; UI stale. Calendar unloadable → no new entries (Phần 03D fail-closed matrix).
