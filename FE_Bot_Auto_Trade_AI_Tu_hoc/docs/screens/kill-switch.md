# Kill-switch

> **In-MVP (mandatory):** L1 pause / emergency pause new entries MUST always be visible
> from monitoring surfaces. See matrix id `emergency-pause`. Higher L2–L4 + SoD are
> release-gate / Phase hardening — do not hide L1 behind menus.

**Blueprint:** Phần 04 Kill-switch; Phần 03D.

## Purpose

Global + scoped L1–L4 control; show dual-control pending (who proposed / who must approve); per account/strategy run state.

## API / WS deps

- REST: `getKillSwitchStatus`, `postKillSwitch` (`x-mvp: true`)
- WS: `kill_switch.*` state fan-out
- Approvals API for resumes requiring SoD

## UX rules

Present on all screens. **L1:** one obvious control for pause new entries. **L3/L4:** confirm + step-up. Never one-click flatten/lockdown. After activate, show execution progress / SLA (L3 ≤30s target). Resume buttons respect SoD (proposer ≠ approver).
