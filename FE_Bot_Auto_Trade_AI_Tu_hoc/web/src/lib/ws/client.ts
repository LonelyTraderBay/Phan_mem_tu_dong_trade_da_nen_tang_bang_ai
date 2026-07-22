/**
 * Gateway WS client — ticket auth, locked paper channels only.
 * Does not invent market data when stale/disconnected.
 */

import { getWsBaseUrl } from "@/lib/api/client";
import { postWsTicket } from "./ticket";
import type { PaperWsChannel, WsEnvelope } from "./types";

export type WsConnectionState = "idle" | "connecting" | "live" | "stale" | "error";

export type PaperWsHandlers = {
  onState?: (state: WsConnectionState, detail?: string) => void;
  onFrame?: (frame: WsEnvelope) => void;
};

const STALE_MS = 15_000;
const DEFAULT_CHANNELS: PaperWsChannel[] = [
  "risk.kill_switch",
  "ops.alerts",
  "trading.orders",
  "trading.positions",
  "market.candles",
];

function joinWsUrl(wsPath: string, ticket: string): string {
  const base = getWsBaseUrl().replace(/\/$/, "");
  // getWsBaseUrl may already include /ws — prefer ticket response path.
  const origin = base.replace(/\/ws\/?$/, "");
  const path = wsPath.startsWith("/") ? wsPath : `/${wsPath}`;
  return `${origin.replace(/^http/, "ws")}${path}?ticket=${encodeURIComponent(ticket)}`;
}

export class PaperWsSession {
  private socket: WebSocket | null = null;
  private staleTimer: ReturnType<typeof setTimeout> | null = null;
  private closed = false;
  private handlers: PaperWsHandlers;
  private channels: PaperWsChannel[];

  constructor(
    handlers: PaperWsHandlers = {},
    channels: PaperWsChannel[] = DEFAULT_CHANNELS,
  ) {
    this.handlers = handlers;
    this.channels = channels;
  }

  async start(): Promise<void> {
    this.closed = false;
    this.handlers.onState?.("connecting");
    const ticketResult = await postWsTicket();
    if (!ticketResult.ok) {
      this.handlers.onState?.(
        "error",
        ticketResult.error.message || "postWsTicket failed",
      );
      return;
    }
    if (this.closed) return;

    const url = joinWsUrl(ticketResult.data.ws_path, ticketResult.data.ticket);
    const socket = new WebSocket(url);
    this.socket = socket;

    socket.onopen = () => {
      this.bumpLive();
      socket.send(
        JSON.stringify({ type: "subscribe", channels: this.channels }),
      );
    };
    socket.onmessage = (ev) => {
      this.bumpLive();
      try {
        const data = JSON.parse(String(ev.data)) as WsEnvelope;
        if (typeof data?.type === "string" && typeof data?.seq === "number") {
          this.handlers.onFrame?.(data);
        }
      } catch {
        // ignore malformed
      }
    };
    socket.onerror = () => {
      this.handlers.onState?.("error", "WebSocket error");
    };
    socket.onclose = () => {
      this.clearStaleTimer();
      if (!this.closed) this.handlers.onState?.("stale", "disconnected");
    };
  }

  stop(): void {
    this.closed = true;
    this.clearStaleTimer();
    this.socket?.close();
    this.socket = null;
    this.handlers.onState?.("idle");
  }

  ping(): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type: "ping" }));
    }
  }

  private bumpLive(): void {
    this.handlers.onState?.("live");
    this.clearStaleTimer();
    this.staleTimer = setTimeout(() => {
      this.handlers.onState?.("stale", "heartbeat silence");
    }, STALE_MS);
  }

  private clearStaleTimer(): void {
    if (this.staleTimer) {
      clearTimeout(this.staleTimer);
      this.staleTimer = null;
    }
  }
}
