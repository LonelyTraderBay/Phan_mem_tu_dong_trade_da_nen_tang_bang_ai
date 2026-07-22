# Release gates (condensed)

Full text: blueprint **Phần 15**. Fail gate = no real money.

## Test pyramid (must-have by phase)

| Layer | From |
|---|---|
| Unit (risk, Kelly, FSM, idempotency) | Phase 1 |
| Adapter contract mocks | Phase 1 |
| Integration Strategy→Risk→OMS + schema | Phase 1 |
| E2E paper | Phase 1 exit |
| Chaos + load + security | Before Phase 2 |
| ML validation (walk-forward, DSR, calibration) | Phase 2+ |

## Chaos minimums

Timeout ack → UNKNOWN (no double order); Risk down → 0 orders; Vault down → 0 new orders; Kafka down → sync path still risk-checks; stale feed → L1 + UI stale; SoD bypass → reject + SEV1 audit.

## Checklists

### Phase 1 → `prod-paper`

- [ ] Kill-switch L1–L4 on staging  
- [ ] Reconciliation job + alerts  
- [ ] 0 secrets in repo  
- [ ] ≥30 days paper criteria (Phần 08)

### Phase 2 → `prod-live` (≤5% NAV)

- [ ] Chaos table PASS  
- [ ] Game-day L3 flatten ≤30s  
- [ ] Restore drill T1 pass (recent quarter)  
- [ ] Security / pen-test PASS  
- [ ] Risk Officer signs 03D limits  
- [ ] Capital sizing in writing  
- [ ] Named on-call rotation

### Phase 3 → auto-retrain / canary

- [ ] Model Cards required  
- [ ] Dual-control promote >10%  
- [ ] OTel ≥95% hot path  
- [ ] Rollback drill &lt;5 minutes

### Phase 4 → multi-user

- [ ] Legal sign-off profile (b) or (c)  
- [ ] Tenant isolation tests PASS  
- [ ] Product ToS + data classification
