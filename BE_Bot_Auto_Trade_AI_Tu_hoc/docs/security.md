# Security (condensed)

Full: blueprint **Phần 13**. Shared SoD: [auth-rbac-sod.md](../shared/auth-rbac-sod.md).

## Musts

- TLS to Gateway; mTLS service-to-service from Phase 3  
- Secrets **only** in Vault/KMS; rotate ≥90d or on incident  
- JWT short TTL + refresh rotation + revoke; step-up for L3/L4 / limits / secrets  
- No secrets in logs, repo, or client bundles  
- SBOM + CVE scan each build; critical patch ≤7 days  
- Audit stream WORM ≥5 years; no delete API on prod  
- Pen-test / security review **PASS** before Phase 2 live  

## Data classes

Secret → Vault; Restricted (positions, orders, P&L, audit) → RBAC + at-rest encryption; Internal config → RBAC; Public → docs/marketing.

Tenant isolation (`tenant_id` on every query) is a Phase 4 gate.
