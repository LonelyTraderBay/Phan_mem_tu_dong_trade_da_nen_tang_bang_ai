# ADR-04 — Strategy → Risk → OMS synchronous

**Status:** Accepted

**Decision:** Sync RPC with timeout and **fail-closed**. Not via Event Bus.

**Why:** Async risk can let orders escape before new limits apply.

**Consequence:** Small latency cost; NFR-01 preserved.
