# Live Monitor

**Blueprint:** Phần 04 Live Monitor; Phần 03C order states.

## Purpose

Realtime candles, signal overlays with calibrated probability, order list including **UNKNOWN**, WS resume-from-sequence.

## API / WS deps

- WS: candles, signals, orders, positions  
- REST: bootstrap snapshot / order detail

## UX rules

**Stale** indicator mandatory on feed gap. Show UNKNOWN distinctly; never fake ACK/FILL. Manual trade actions confirm + wait for server state.
