# Kill-switch

**Blueprint:** Phần 04 Kill-switch; Phần 03D.

## Purpose

Global + scoped L1–L4 control; show dual-control pending (who proposed / who must approve); per account/strategy run state.

## API / WS deps

- REST: activate/resume kill-switch, list scopes  
- WS: `kill_switch.*` state fan-out  
- Approvals API for resumes requiring SoD

## UX rules

Present on all screens. **L3/L4:** confirm + step-up. Never one-click flatten/lockdown. After activate, show execution progress / SLA (L3 ≤30s target). Resume buttons respect SoD (proposer ≠ approver).
