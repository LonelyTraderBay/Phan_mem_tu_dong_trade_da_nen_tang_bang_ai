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

Tracking feature: [`specs/003-prod-paper-harden/`](../../specs/003-prod-paper-harden/) · assignment `PROD-PAPER-HARDEN`.

- [x] Kill-switch L1–L4 on staging — *tooling done in 003 / RFC-0002 (paper/dev; re-run on staging env)*  
- [x] Reconciliation job + alerts — *module + `RECON_MISMATCH` alerts (003)*  
- [x] 0 secrets in repo — *validate_governance + gitleaks config PASS (ongoing)*  
- [x] ~~≥30 days paper criteria (Phần 08)~~ — **waived as Pass requirement** — *Owner amend 2026-07-23 (option B): remove calendar gate; [paper-ops-tracker.md](./paper-ops-tracker.md) is **optional ops log only***

### Phase 2 → `prod-live` (≤5% NAV)

Docs + paper tooling (not live capital):

- Chaos: [`chaos-checklist.md`](./chaos-checklist.md) · [`006`](../../specs/006-prod-live-chaos-docs/)
- Remaining pack: [`phase2-remaining-gates.md`](./phase2-remaining-gates.md) · [`007`](../../specs/007-phase2-remaining-gates-docs/)
- Evidence registry: [`phase2-evidence-registry.md`](./phase2-evidence-registry.md) · drills [`008`](../../specs/008-phase2-staging-drills/)
- Sign-off templates: [`phase2-signoff/`](./phase2-signoff/)

- [x] Chaos table PASS — *Owner 2026-07-23 auto-check: paper tooling surrogate; see [phase2-owner-auto-check.md](./phase2-owner-auto-check.md)*  
- [x] Game-day L3 flatten ≤30s — *paper L3 tooling PASS; Owner accepted surrogate*  
- [x] Restore drill T1 pass (recent quarter) — *Owner self-attest paper restart+smoke surrogate*  
- [x] Security / pen-test PASS — *Owner self-attest review (no external firm); residual risk accepted*  
- [x] Risk Officer signs 03D limits — *Owner acting Risk; capital policy + KS*  
- [x] Capital sizing in writing — *≤5% NAV ceiling; `LIVE_NAV_QUOTE` at live-enable*  
- [x] Named on-call rotation — *solo Owner roster*

### Phase 3 → auto-retrain / canary

- [ ] Model Cards required  
- [ ] Dual-control promote >10%  
- [ ] OTel ≥95% hot path  
- [ ] Rollback drill &lt;5 minutes

### Phase 4 → multi-user

> **MVP matrix:** `multi-user-saas` is **Deferred (phase-4)** and remains **legally gated**.
> Do not implement multi-tenant third-party capital without legal sign-off + Owner amend of the matrix.

- [ ] Legal sign-off profile (b) or (c)  
- [ ] Tenant isolation tests PASS  
- [ ] Product ToS + data classification
- [ ] Owner amend MVP matrix Deferred → In-MVP (if ever)
