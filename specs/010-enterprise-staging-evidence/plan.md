# Plan: 010 Enterprise staging evidence

## Constitution Check

- Contract-first: no new public REST/WS shapes.
- Fail-closed / capital safety: unchanged; evidence only.
- Lane: BE gateway scripts + docs/shared only.
- No secrets in evidence output.

## Design

1. `scripts/export_phase2_evidence.py` — pytest junitxml → `artifacts/phase2-evidence/`.
2. `docs/shared/phase2-staging-runbook.md` — SRE steps.
3. Wire registry + assignment close.
