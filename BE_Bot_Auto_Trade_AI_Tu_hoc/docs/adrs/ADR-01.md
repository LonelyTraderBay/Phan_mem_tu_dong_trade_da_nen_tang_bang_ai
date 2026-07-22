# ADR-01 — Event Bus: Kafka vs Redis Streams

**Status:** Accepted (blueprint Phần 12)

**Decision:** Kafka (or managed equivalent / Redpanda-compatible) for core durable events. Redis only for non-audit ephemeral signals/cache.

**Why:** Replay + consumer groups + audit (NFR-02).

**Consequence:** Higher ops cost; schema registry mandatory.
