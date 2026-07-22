# Quickstart: Paper Trading E2E

## Prerequisites

- Repo root with `specs/002-paper-trading-e2e/`
- `P1-*-PAPER-STUB` waves completed (Gateway stubs + FE screens)
- PyYAML + gateway editable install; FE `npm install` in `web/`
- `.\scripts\validate-contracts.ps1` → PASS

## 1. Validate governance

```powershell
.\scripts\validate-contracts.ps1
```

## 2. Run Gateway tests + smoke

```powershell
cd BE_Bot_Auto_Trade_AI_Tu_Hoc\services\gateway
python -m pytest -q
python scripts\wave9_smoke.py
```

Extend smoke during implement to assert at least one paper order/risk outcome (task TBD in tasks.md).

## 3. Run FE typecheck

```powershell
cd FE_Bot_Auto_Trade_AI_Tu_Hoc\web
npx tsc --noEmit
```

## 4. Manual paper-day (acceptance)

1. Login (`operator@example.com` / env paper password)
2. Create account + API key (masked)
3. Create strategy → activate (risk up)
4. Observe paper order/position/report updates
5. Engage L1 pause → confirm no new entries
6. Set risk unavailable → activate blocked (fail-closed)
7. Review reports/alerts

**Automated record (T023):** `python scripts/wave9_smoke.py` → **WAVE9_SMOKE PASS** on 2026-07-22
(positions/trades after activate; L1 alert; fail-closed 503).

## Out of scope

- Live capital, MT5-first, no-code, AI promote, multi-user SaaS
