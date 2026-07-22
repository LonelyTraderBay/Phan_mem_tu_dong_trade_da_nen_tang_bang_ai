# ADR-09 — Exit MetaApi → EA bridge

**Status:** Accepted

**Decision:** Move to EA bridge (or hybrid) when any trigger hits: MetaApi monthly cost over CTO threshold; unacceptable credential/ToS incident; MT5 account count ≥ N (set in Phase 0). Prototype EA bridge **before** crossing threshold.

**Why:** Avoid vendor lock + third-party secret risk growth.

**Consequence:** Clear exit ramp; dual path until cutover.
