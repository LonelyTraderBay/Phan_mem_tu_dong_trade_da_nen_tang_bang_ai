# AI Model Center

**Blueprint:** Phần 04 AI Model Center; Phần 05 MRM.

## Purpose

List model versions, PSR/DSR, live calibration, Model Cards; champion/challenger/shadow/canary; drift logs; retrain / promote actions.

## API / WS deps

- REST: models list, cards, retrain trigger, promote  
- WS: training job progress; model lifecycle events (via Gateway fan-out)

## UX rules

Promote &gt;10% NAV → Approvals / dual-control. Disable self-approve. Show rollback status clearly. Never imply auto-100% promote.
