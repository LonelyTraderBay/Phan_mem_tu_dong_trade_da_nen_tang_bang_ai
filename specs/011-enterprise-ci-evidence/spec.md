# Feature Spec: Enterprise CI tooling evidence

## Overview

Owner activated `ENTERPRISE-CI-EVIDENCE`: CI must run `export_phase2_evidence.py`, fail the job on `tooling_FAIL`, and upload evidence artifacts. Must not tick release-gates Pass, enable live keys, add mainnet adapter, or implement Deferred.

## Requirements

- FR-001: GitHub Actions job on PR/push installs gateway deps and runs the exporter.
- FR-002: Job fails when exporter exits non-zero or any drill is not tooling_PASS.
- FR-003: Upload `evidence-latest.json`, `evidence-latest.md`, and junit XML as artifacts.
- FR-004: Docs note that CI tooling Pass ≠ gate Pass.

## Out of scope

- Auto-updating `release-gates.md`, live/mainnet, Deferred, G-02…G-06 human sign-off.
