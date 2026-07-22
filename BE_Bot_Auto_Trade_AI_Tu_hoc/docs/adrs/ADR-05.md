# ADR-05 — TimescaleDB vs InfluxDB

**Status:** Accepted

**Decision:** TimescaleDB (Postgres extension) for market/feature time-series baseline.

**Why:** SQL + JOINs with ledger Postgres; one ops model.

**Consequence:** Revisit Influx only if extreme cardinality demands it later.
