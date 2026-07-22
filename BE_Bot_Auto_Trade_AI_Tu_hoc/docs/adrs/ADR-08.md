# ADR-08 — Default reporting currency USD

**Status:** Accepted

**Decision:** Consolidated equity/P&L in USD; optional VND report using FX rate stored at event time.

**Why:** Multi-market instruments need one reporting currency.

**Consequence:** Trusted FX source; every fee/trade stores `fx_rate` + `amount_reporting`.
