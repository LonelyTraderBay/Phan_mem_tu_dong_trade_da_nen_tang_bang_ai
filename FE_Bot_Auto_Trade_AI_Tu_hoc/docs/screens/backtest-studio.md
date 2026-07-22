# Backtest Studio

**Blueprint:** Phần 04 Backtest Studio.

## Purpose

Submit async backtests (range, capital, fees, slippage); show equity/drawdown; compare runs with PSR/DSR.

## API / WS deps

- REST: create job, fetch results  
- WS: job progress / completion

## UX rules

Jobs may take minutes — progress UI required. Do not treat backtest P&L as live portfolio. Surface fee/slippage assumptions from API, not hard-coded client defaults that diverge from contracts.
