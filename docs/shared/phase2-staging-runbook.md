# Phase-2 staging runbook (C-01…C-06 + G-01)

**Assignment:** `ENTERPRISE-STAGING-EVIDENCE`  
**Scope:** paper/staging **tooling evidence** + how SRE re-runs on a real host.  
**Cấm:** tick [release-gates.md](./release-gates.md) Pass từ output máy; live keys; mainnet adapter.

Canonical checklists: [chaos-checklist.md](./chaos-checklist.md) · [phase2-remaining-gates.md](./phase2-remaining-gates.md) (G-01).

---

## 1. Paper local (machine evidence)

Prereq: Python env for Gateway; no production secrets.

```powershell
cd BE_Bot_Auto_Trade_AI_Tu_Hoc\services\gateway
python scripts\export_phase2_evidence.py
```

Artifacts (gitignored):

- `artifacts/phase2-evidence/evidence-latest.json`
- `artifacts/phase2-evidence/evidence-latest.md`
- `artifacts/phase2-evidence/junit-drills.xml`

Expect: `summary.tooling_pass == 7`, `release_gates_auto_tick == false`, every drill `gate_pass: false`.

Attach `evidence-latest.md` (or JSON) to the ops ticket. **Do not** copy results into release-gates as Pass.

### CI (automatic on PR/push)

Workflow: `.github/workflows/phase2-tooling-evidence.yml`  
- Runs the same exporter; **fails the job** if any drill is not `tooling_PASS`.  
- Uploads artifact `phase2-tooling-evidence` (JSON/MD/junit).  
- Still **not** release-gates Pass.

---

## 2. Staging host (human evidence — required for gate Pass)

Use paper/demo broker only. Record `trace_id` / audit ids — never API secrets.

| ID | Inject on staging | Capture | Sign-off |
|---|---|---|---|
| C-01 | Drop/delay venue ack after submit | Order → UNKNOWN; no blind resubmit; venue query before retry | SRE |
| C-02 | Force Risk unavailable | 0 new entries; operator-visible reject | SRE + Risk |
| C-03 | Vault / secrets path down | 0 new orders; logs scrubbed | SRE |
| C-04 | Break async bus (if present) or note N/A monolith | Sync risk-check still recorded | SRE |
| C-05 | Silence market feed beyond SLA | L1 / entries blocked; UI stale | SRE + FE check |
| C-06 | Same actor attempts L2+ without dual-control | Reject + SEV1-class audit | SRE + Security |
| G-01 | Engage L3 with open orders | Flatten/cancel complete ≤30s wall-clock | SRE + Risk |

Fill Pass/Fail columns in [chaos-checklist.md](./chaos-checklist.md) and G-01 steps in [phase2-remaining-gates.md](./phase2-remaining-gates.md).

G-02…G-06 remain separate templates under [phase2-signoff/](./phase2-signoff/) — **out of this assignment scope**.

---

## 3. When may Owner tick release-gates?

Only after **staging** rows above are Pass with named sign-off + dates.  
Paper `export_phase2_evidence.py` alone is **insufficient**.

---

## 4. Related

- Registry: [phase2-evidence-registry.md](./phase2-evidence-registry.md)
- Capital envelope (not this wave): [prod-live-capital-policy.md](./prod-live-capital-policy.md)
