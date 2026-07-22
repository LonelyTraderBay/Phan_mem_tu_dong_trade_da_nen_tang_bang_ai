# AI Model Center

> **Out of MVP:** Promote / auto-retrain UI is **Deferred** — matrix
> `ai-auto-retrain-promote` (phase-3). Do not present as live MVP capability.
> Contract stub `postModelPromote` is `x-mvp: false`.

**Blueprint:** Phần 04 AI Model Center; Phần 05 MRM.

## Purpose

List model versions, PSR/DSR, live calibration, Model Cards; champion/challenger/shadow/canary; drift logs; retrain / promote actions.

## API / WS deps

- REST: models list, cards, retrain trigger, promote (Deferred for MVP day)
- WS: training job progress; model lifecycle events (via Gateway fan-out)

## UX rules

Promote &gt;10% NAV → Approvals / dual-control. Disable self-approve. Show rollback status clearly. Never imply auto-100% promote. For Phase 1 paper day: hide or clearly label “Not in MVP”.
