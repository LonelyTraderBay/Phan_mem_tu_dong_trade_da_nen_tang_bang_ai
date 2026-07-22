# Vault (Phase later)

HashiCorp Vault (or cloud KMS equivalent) holds broker API keys, MT5 credentials, and other secrets.

## Phase guidance

- Phase 1: may use local/dev secret injection via Compose env for **non-prod** only — still never commit secrets.  
- Phase 2+ live: Vault HA required (DR T0); AppRole/mTLS; audit every secret read.  
- Fail-closed: Vault unreachable → no new orders / no new credential reads (blueprint 03D / 14).

## Out of scope for this scaffold

No Vault server in Compose yet. Wire when Security gate for Phase 2 starts.
