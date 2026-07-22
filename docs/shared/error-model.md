# Error model

All Gateway error responses use one JSON shape (also mirrored in OpenAPI components).

```json
{
  "code": "RISK_REJECTED",
  "message": "Human-readable summary",
  "trace_id": "uuid",
  "details": [
    { "field": "optional.path", "reason": "optional machine hint" }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `code` | yes | Stable snake/SCREAMING token; FE maps UX by code, not by message text |
| `message` | yes | Safe for UI; no secrets |
| `trace_id` | yes | Correlate with OTel / audit |
| `details` | no | Array; empty if unused |

## Conventions

- Prefer **domain codes** (`RISK_REJECTED`, `KILL_SWITCH_ACTIVE`, `DUAL_CONTROL_PENDING`, `IDEMPOTENCY_CONFLICT`, `STALE_DATA`) over generic HTTP-only messaging.
- HTTP status still set correctly (4xx client, 5xx server, 501 stub).
- Never put secrets, passwords, or full broker payloads in `message` / `details`.
