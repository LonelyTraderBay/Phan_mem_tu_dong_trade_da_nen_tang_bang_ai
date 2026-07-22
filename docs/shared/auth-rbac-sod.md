# Auth, RBAC & SoD

Canonical detail: blueprint **Phần 03D** (limits/kill-switch) + **Phần 13** (security). Roles file: `packages/contracts/rbac/roles.yaml`.

## Roles

| Role | Typical powers |
|---|---|
| `admin` | Broad ops; L3/L4 with step-up; cannot self-approve SoD |
| `trader` | Configure strategies, propose risk-limit changes, monitor |
| `viewer` | Read-only |
| `risk_officer` | Approve limits, resume L2+/L3, promote canary >10% NAV |
| `ml_lead` | Retrain / promote models (SoD with risk_officer when capital >10%) |
| `sre` | Ops, resume L2 propose, break-glass (TTL ≤60m) |

Break-glass: TTL ≤60 minutes, SEV1 audit, post-review ≤24h.

## Auth mechanics (Gateway)

- Short-lived JWT + refresh rotation + revoke list  
- Step-up auth for L3/L4, risk-limit change, secret export, break-glass  
- API keys / broker secrets: Vault/KMS only — never plaintext in logs or repo

## Dual-control (SoD) summary

| Action | Proposer | Approver |
|---|---|---|
| Change risk limit | trader / admin | risk_officer |
| Resume L2 (account+) | sre / admin | risk_officer |
| Manual L3 | admin / risk_officer | step-up (same actor OK in SEV1) |
| Resume L3 | admin | risk_officer |
| L4 activate / resume | admin **or** risk_officer | the other (two-person) |
| Promote canary → 100% | ml_lead | risk_officer if canary >10% NAV |

**Proposer ≠ approver** on the same request (except documented break-glass).
