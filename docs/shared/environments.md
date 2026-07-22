# Environments

| Env | Purpose | Data | Promote rule |
|---|---|---|---|
| `dev` | Local / CI | Synthetic + public history | Free |
| `staging` | Integration, chaos, game-day | Paper / demo broker | Green CI + review |
| `prod-paper` | Long-running paper | Paper keys | Phase 1 checklist ([release-gates](./release-gates.md)) |
| `prod-live` | Real capital | Live keys in Vault | Dual gate: Risk + SRE + Security |

Config: Infrastructure-as-Code / Config-as-Code (Compose + Git in Phase 1; GitOps from Phase 3).

**Never** commit live secrets. Use root `.env.example` as the non-secret template only.
