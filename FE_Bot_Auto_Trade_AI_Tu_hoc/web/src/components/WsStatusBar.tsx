"use client";

import { useEffect, useState } from "react";
import { hasAccessToken } from "@/lib/auth/tokenStore";
import {
  PaperWsSession,
  type WsConnectionState,
} from "@/lib/ws/client";
import type { WsEnvelope } from "@/lib/ws/types";

/**
 * Always-visible paper WS status. Marks stale on silence/disconnect.
 * Does not invent market data — only shows connection + last kill-switch hint.
 */
export function WsStatusBar() {
  const [state, setState] = useState<WsConnectionState>("idle");
  const [detail, setDetail] = useState<string | null>(null);
  const [killHint, setKillHint] = useState<string | null>(null);

  useEffect(() => {
    if (!hasAccessToken()) {
      setState("idle");
      setDetail("login for realtime");
      return;
    }

    const session = new PaperWsSession({
      onState: (s, d) => {
        setState(s);
        setDetail(d ?? null);
      },
      onFrame: (frame: WsEnvelope) => {
        if (frame.channel === "risk.kill_switch" && frame.payload) {
          const engaged = frame.payload.engaged === true;
          const level =
            typeof frame.payload.level === "string"
              ? frame.payload.level
              : null;
          setKillHint(
            engaged ? `${level ?? "L?"} ENGAGED (ws)` : "open (ws)",
          );
        }
      },
    });
    void session.start();
    const pingId = setInterval(() => session.ping(), 10_000);
    return () => {
      clearInterval(pingId);
      session.stop();
    };
  }, []);

  const label =
    state === "live"
      ? "WS live"
      : state === "connecting"
        ? "WS connecting…"
        : state === "stale"
          ? "WS stale"
          : state === "error"
            ? "WS error"
            : "WS idle";

  const className =
    state === "live"
      ? "border-emerald-600 bg-emerald-50 text-emerald-950"
      : state === "stale" || state === "error"
        ? "border-amber-600 bg-amber-50 text-amber-950"
        : "border-neutral-300 bg-neutral-50 text-neutral-700";

  return (
    <div
      className={`border-b px-4 py-1 text-xs ${className}`}
      role="status"
      aria-live="polite"
    >
      <div className="mx-auto flex max-w-5xl flex-wrap gap-3">
        <strong className="font-semibold">{label}</strong>
        {detail ? <span>{detail}</span> : null}
        {killHint ? <span>· kill-switch {killHint}</span> : null}
        <span className="text-neutral-500">
          Gateway only — no invented ticks when stale
        </span>
      </div>
    </div>
  );
}
