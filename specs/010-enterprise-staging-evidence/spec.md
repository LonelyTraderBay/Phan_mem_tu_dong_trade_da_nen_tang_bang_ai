# Feature Spec: Enterprise staging evidence export

## Overview

Owner activated `ENTERPRISE-STAGING-EVIDENCE`: export machine-readable **paper/staging tooling evidence** for chaos **C-01…C-06** and game-day **G-01**, plus an SRE runbook. This does **not** mark release-gates Pass, enable live keys, implement mainnet, or Deferred capabilities.

## Requirements

- FR-001: Script re-runs drill suite and writes JSON + Markdown evidence pack with per-ID results.
- FR-002: Pack MUST label results as `tooling` (not `gate_pass`).
- FR-003: Runbook documents how to run on paper local and staging host; human sign-off still required for Pass.
- FR-004: Update evidence registry to point at exporter; never auto-tick `release-gates.md`.

## Out of scope

- Live/mainnet adapter, Phase-2 human signoffs G-02…G-06 Pass ticks, Deferred matrix items.
