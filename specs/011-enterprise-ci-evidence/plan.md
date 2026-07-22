# Plan: 011 Enterprise CI evidence

## Constitution Check

- No new public contracts.
- Fail-closed unchanged; CI only enforces paper drill tooling.
- Paths: `.github/workflows/`, gateway (reuse exporter), `docs/shared/`, specs.

## Design

New workflow `phase2-tooling-evidence.yml` → pip install gateway[dev] → `python scripts/export_phase2_evidence.py` → assert JSON summary → `actions/upload-artifact`.
