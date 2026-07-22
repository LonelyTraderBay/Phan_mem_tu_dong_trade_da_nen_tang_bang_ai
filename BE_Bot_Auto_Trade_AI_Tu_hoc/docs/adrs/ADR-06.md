# ADR-06 — Feature Store: build vs Feast

**Status:** Accepted

**Decision:** Phase 1–2 thin versioned store on Postgres/Timescale; evaluate Feast in Phase 3 if feature/team scale warrants.

**Why:** Faster MVP, lower ops.

**Consequence:** Keep a clean interface so Feast swap does not rewrite Inference.
