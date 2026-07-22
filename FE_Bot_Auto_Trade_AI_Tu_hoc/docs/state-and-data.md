# State & data

## Principles

- Server is source of truth for positions, orders, P&L, risk, approvals.  
- Client cache (React Query / similar) for REST; WS patches invalidate or merge by `seq`.  
- Auth tokens: secure storage; refresh via Gateway; revoke on logout.

## Data paths

| Need | Transport |
|---|---|
| Config / mutations | REST `/v1` + Idempotency-Key where required |
| Live market / orders / KS / alerts | WS (+ resume `last_seq`) |
| Historical reports | REST paginated / CSV download |

## Stale & gaps

- If WS gap warning or heartbeat miss → mark channel stale; banner per [ux-rules](./ux-rules.md).  
- Do not extrapolate prices. Re-snapshot on reconnect when replay insufficient.

## Environment

Use `NEXT_PUBLIC_*` only for non-secret endpoints. No broker secrets in the browser beyond masked status from API.
