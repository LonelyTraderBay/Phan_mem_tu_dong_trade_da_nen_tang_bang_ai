/** Gateway WS envelope — packages/contracts/ws/ws-protocol.md (RFC-0003). */

export const PAPER_WS_CHANNELS = [
  "market.candles",
  "trading.orders",
  "trading.positions",
  "risk.kill_switch",
  "ops.alerts",
] as const;

export type PaperWsChannel = (typeof PAPER_WS_CHANNELS)[number];

export type WsTicketResponse = {
  ticket: string;
  expires_at: string;
  ws_path: string;
};

export type WsEnvelope = {
  type: string;
  channel?: string;
  seq: number;
  produced_at_utc: string;
  stale?: boolean;
  trace_id?: string | null;
  payload?: Record<string, unknown>;
};

export function parseWsTicket(data: unknown): WsTicketResponse | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.ticket !== "string" || o.ticket.length < 16) return null;
  if (typeof o.expires_at !== "string") return null;
  if (typeof o.ws_path !== "string" || !o.ws_path.startsWith("/")) return null;
  return {
    ticket: o.ticket,
    expires_at: o.expires_at,
    ws_path: o.ws_path,
  };
}
