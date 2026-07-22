# ADR-07 — LLM sentiment off hot path

**Status:** Accepted

**Decision:** Claude/LLM sentiment is async auxiliary feature; Inference never waits on LLM.

**Why:** Latency, cost, availability risk must not break candle cycle.

**Consequence:** Weaker news edge; stable latency/FinOps. Missing sentiment ≠ invent a guess.
