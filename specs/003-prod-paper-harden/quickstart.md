# Quickstart: Prod-Paper Harden

## 0. Prerequisites

- Demo auth from 002 still works (`operator@example.com` / paper password).
- Gateway pytest baseline green; `.\scripts\validate-contracts.ps1` PASS after contract RFC lands.
- Assignment `PROD-PAPER-HARDEN` is `active` and named by Owner in chat.

## 1. Contracts

1. Ensure RFC for kill-switch `level` (+ `confirmed`) is approved/landed in `packages/contracts`.
2. Run `.\scripts\validate-contracts.ps1` → **RESULT: PASS**.

## 2. Kill-switch L1–L4 (staging/dev)

1. Login → note KillSwitchBar shows level when engaged.
2. Engage **L1** → activate strategy entry path blocked.
3. Attempt **L2** without `confirmed` → rejected.
4. Engage **L2** with confirm → status shows L2; entries still blocked.
5. Engage **L3** / **L4** with confirm (paper-internal cancel/flatten) → no live exchange claim.
6. Disengage per rules → status clear.

## 3. Reconciliation

1. With matched books → run recon (job or dev trigger) → no critical `RECON_MISMATCH`.
2. Force mismatch in test → `RECON_MISMATCH` alert visible on alerts UI.

## 4. Secrets + paper-ops

1. Confirm governance/gitleaks still PASS.
2. Open `docs/shared/paper-ops-tracker.md` and record operator progress toward ≥30-day paper (Owner calendar — not CI).

## 5. Stop

Do not start `PAPER-TESTNET-ADAPTER` until this assignment is `done` and Owner activates the next id.
