# Chaos checklist (Phase 2 → `prod-live` gate)

**Canonical gates:** [release-gates.md](./release-gates.md) · [phase2-owner-auto-check.md](./phase2-owner-auto-check.md)  
**Environments:** staging preferred; Owner 2026-07-23 accepted **paper Gateway tooling** as staging surrogate (solo).

Fail any row below ⇒ **không** mở vốn thật (unless Owner amend).

---

## How to use

1. Run drills (staging or Owner-accepted paper surrogate).
2. Record Pass/Fail + evidence (`trace_id`, audit, exporter pack).
3. Sign-off = named role — AI only when Owner authorized auto-check.
4. When all rows Pass, Owner may tick “Chaos table PASS” in [release-gates.md](./release-gates.md).

---

## Chaos minimum table

| ID | Inject (fault) | Expected system behavior | Evidence to capture | Pass? | Sign-off | Date / notes |
|---|---|---|---|---|---|---|
| C-01 | **Timeout ack** / no blind double submit | No double fill on re-activate | `export_phase2_evidence` C-01 tooling_PASS | [x] | Owner (AI auto-check) | 2026-07-23 paper surrogate |
| C-02 | **Risk down** | 0 new entries | tooling_PASS + paper UI fail-closed | [x] | Owner (AI auto-check) | 2026-07-23 |
| C-03 | **Vault / credentials down** | 0 new orders | tooling_PASS credentials_required | [x] | Owner (AI auto-check) | 2026-07-23 |
| C-04 | **Bus down** (N/A monolith) | Sync risk-check still runs | tooling_PASS C-04 | [x] | Owner (AI auto-check) | 2026-07-23 N/A monolith |
| C-05 | **Stale feed** + L1 | Entries blocked; stale UX | tooling_PASS C-05 | [x] | Owner (AI auto-check) | 2026-07-23 |
| C-06 | **SoD / L2 without confirm** | Reject | tooling_PASS C-06 | [x] | Owner (AI auto-check) | 2026-07-23 |

---

## Paper vs live caution

- Paper tooling ≠ exchange mainnet chaos.
- Owner accepted paper surrogate for this solo Phase-2 closeout ([phase2-owner-auto-check.md](./phase2-owner-auto-check.md)).
- Live keys still require live adapter assignment after gates.
