# ADR-02 — Modular-monolith vs full microservices (Phase 1)

**Status:** Accepted

**Decision:** Group modules into few containers (Core Trading, Data, AI, Backtest, Gateway) in Phase 1; split later by measured load (Phase 3–4).

**Why:** 15 services too early/expensive.

**Consequence:** Enforce module boundaries in code from day one.
