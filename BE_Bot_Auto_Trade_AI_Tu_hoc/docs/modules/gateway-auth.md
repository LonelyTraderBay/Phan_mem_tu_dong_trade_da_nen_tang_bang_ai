# Gateway & Auth

**Blueprint:** Phần 03 — API Gateway & Auth; Phần 13.

## Responsibility

Sole FE entrypoint: JWT auth, RBAC, rate limits, OpenAPI `/v1`, step-up for dangerous mutations, vault-backed broker key ingest (never plaintext logs).

## Phase

Independent container from **Phase 1**.

## Interfaces

- In: FE REST + WS  
- Out: internal services (not exposed to FE)  
- Contracts: OpenAPI, WS, RBAC, error model

## Fail-closed notes

Auth/revoke unavailable → deny mutations. Vault down → no new credential reads / no new orders depending on policy. Idempotency-Key required on dangerous POSTs.
