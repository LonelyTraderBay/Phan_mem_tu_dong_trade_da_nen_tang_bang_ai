# Paper-ops tracker (≥30-day criteria)

**Purpose**: Operator/Owner record progress toward Phase 1 → `prod-paper` “≥30 days paper” gate (`docs/shared/release-gates.md`).  
**Not** completed by CI or a single implement session.

| Criterion | Target | Recorded | Last reviewed | Notes |
|---|---|---|---|---|
| Consecutive paper operating days | ≥30 | 0 | 2026-07-22 | Start after prod-paper harden tooling lands |
| Kill-switch drill L1–L4 (staging) | Pass once | tooling PASS (dev) | 2026-07-22 | Re-run on real staging host |
| Reconciliation mismatch alert drill | Pass once | tooling PASS (tests) | 2026-07-22 | Feature 003 |
| Zero secrets incident in repo | Ongoing | governance PASS | 2026-07-22 | gitleaks + validate_governance |
| No unexplained ledger drift | Ongoing | pending | | After recon job |

Owner updates **Recorded** / **Last reviewed** manually.
