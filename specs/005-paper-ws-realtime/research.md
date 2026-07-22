# Research: Paper WS Realtime

### D1 — Ticket via REST then query param

Matches existing FE `NEXT_PUBLIC_WS_URL` pattern; OpenAPI documents `ws_path`.

### D2 — Lock five paper channels (RFC-0003)

Align protocol table; drop example drift (`market.ticks` / `orders.updates`).

### D3 — In-memory hub for Phase 1

Sufficient for single Gateway paper process; no Redis required yet.

### D4 — Minimal resume

Emit `gap` when `last_seq` behind buffer; send kill-switch snapshot on subscribe.
