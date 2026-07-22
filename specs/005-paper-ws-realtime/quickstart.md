# Quickstart: Paper WS Realtime

1. Login → `POST /v1/ws/ticket` with Bearer.
2. Connect `ws://localhost:8000/ws?ticket=...`
3. Send `{"type":"subscribe","channels":["risk.kill_switch","trading.orders"]}`
4. Engage L1 via REST → receive `risk.kill_switch` frame.
5. FE: layout shows WS connected/stale via `WsStatusBar`.

```text
cd BE_Bot_Auto_Trade_AI_Tu_Hoc/services/gateway
python -m pytest tests/test_ws_realtime.py -q
```
