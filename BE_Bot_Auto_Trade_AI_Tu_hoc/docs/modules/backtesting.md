# Backtesting Engine

**Blueprint:** Phần 03 Backtesting; Phần 05 metrics.

## Responsibility

Async historical sims with fee/slippage matching live Fee Model; Sharpe/Sortino/MaxDD/win rate + PSR/DSR; walk-forward purge/embargo. Isolated from trading hot path.

## Phase

Own container from Phase 1.

## Interfaces

- In: Gateway job API  
- Out: job status WS/REST; artifacts for Model Center / Strategy compare  
- Same fee contract as live adapters

## Fail-closed notes

Job failure must not affect live OMS. Results without fee model alignment are not promote-eligible.
