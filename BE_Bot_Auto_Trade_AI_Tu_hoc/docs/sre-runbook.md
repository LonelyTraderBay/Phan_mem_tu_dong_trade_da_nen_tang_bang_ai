# SRE runbook (condensed)

Full: blueprint **Phần 11**.

## SLO highlights

| Service | Target |
|---|---|
| OMS submit→ack | p99 &lt; 500ms |
| Risk check | p99 &lt; 200ms |
| Gateway uptime (market hours) | ≥ 99.9% |
| Inference latency | p99 &lt; 50% candle period |
| Reconciliation | every 1–5 min when positions open |

**Error budget (30d):** 0.1% hot-path downtime. &lt;25% left → freeze high-risk change; exhausted → SEV1 hotfixes only.

## Alert SEV

| SEV | Examples | Channel |
|---|---|---|
| 1 | Auto kill-switch, recon break, disconnect with open positions, break-glass | Page |
| 2 | Stale symbol, broker errors with fallback, calibration drift | Chat |
| 3 | Successful promote, digests | Digest |

## Mini playbooks

- **Recon break:** L2 → SEV1 → broker is truth → fix ledger → audit → RESOLVED.  
- **Kill-switch:** execute level → L3/L4 = SEV1 → resume only via SoD.  
- **Broker maintenance:** L1 before window → resume when healthy.  
- **DR:** follow [dr-bcp.md](./dr-bcp.md); do not invent on prod-live.  
- **Postmortem:** every SEV1 within 5 business days (blameless).

On-call: named primary; Phase 2+ secondary for SEV1; break-glass TTL ≤60m.
