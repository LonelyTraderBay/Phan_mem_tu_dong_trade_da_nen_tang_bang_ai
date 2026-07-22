"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  formatApiFailureForUi,
  getKillSwitchStatus,
  postKillSwitch,
} from "@/lib/kill-switch/api";
import type { KillSwitchStatus } from "@/lib/kill-switch/types";
import { hasAccessToken } from "@/lib/auth/tokenStore";

const HIGHER_LEVELS = ["L2", "L3", "L4"] as const;

/**
 * Always-visible L1 emergency pause (layout header — never buried in menus).
 * Mutate only after window.confirm. Engaged state from getKillSwitchStatus API.
 * L2–L4 disabled (not In-MVP contract shape).
 */
export function KillSwitchBar() {
  const router = useRouter();
  const [status, setStatus] = useState<KillSwitchStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageKind, setMessageKind] = useState<"ok" | "err" | "stub" | null>(
    null,
  );
  const [authed, setAuthed] = useState(false);

  const loadStatus = useCallback(async () => {
    if (!hasAccessToken()) {
      setAuthed(false);
      setStatus(null);
      return;
    }
    setAuthed(true);
    const result = await getKillSwitchStatus();
    if (!result.ok) {
      setStatus(null);
      setMessageKind(
        result.kind === "stub_not_implemented" ? "stub" : "err",
      );
      setMessage(formatApiFailureForUi(result));
      if (result.kind === "unauthorized") {
        setAuthed(false);
        router.replace("/login");
      }
      return;
    }
    setMessageKind(null);
    setMessage(null);
    setStatus(result.data);
  }, [router]);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  async function onToggleL1() {
    if (busy) return;

    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }

    const nextEngaged = !(status?.engaged ?? false);
    const actionLabel = nextEngaged
      ? "PAUSE new entries (L1 engage)"
      : "RESUME new entries (L1 disengage)";
    const confirmed = window.confirm(
      `Confirm kill-switch L1: ${actionLabel}?\n\nThis calls postKillSwitch.`,
    );
    if (!confirmed) return;

    const reason = window.prompt(
      "Reason (required):",
      nextEngaged ? "Operator L1 emergency pause" : "Operator L1 resume",
    );
    if (reason === null) return;
    const trimmed = reason.trim();
    if (trimmed.length === 0) {
      setMessageKind("err");
      setMessage("Reason is required to change kill-switch.");
      return;
    }

    setBusy(true);
    setMessage(null);
    setMessageKind(null);
    const result = await postKillSwitch({
      engaged: nextEngaged,
      reason: trimmed.slice(0, 500),
    });
    setBusy(false);

    if (!result.ok) {
      setMessageKind(
        result.kind === "stub_not_implemented" ? "stub" : "err",
      );
      setMessage(formatApiFailureForUi(result));
      if (result.kind === "unauthorized") {
        setAuthed(false);
        router.replace("/login");
      }
      return;
    }

    setStatus(result.data);
    setMessageKind("ok");
    setMessage(
      result.data.engaged
        ? "L1 engaged — new entries paused (server)."
        : "L1 disengaged — new entries allowed subject to risk (server).",
    );
  }

  const engaged = status?.engaged === true;

  return (
    <header className="border-b border-neutral-200 bg-white">
      {engaged ? (
        <div
          role="status"
          className="border-b border-red-700 bg-red-600 px-4 py-1 text-center text-xs font-semibold text-white"
        >
          L1 ENGAGED — new entries paused (from API)
          {status?.updated_at ? ` · updated_at ${status.updated_at}` : ""}
        </div>
      ) : null}
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3 px-4 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Kill switch
        </span>

        <button
          type="button"
          onClick={() => void onToggleL1()}
          disabled={busy || !authed}
          className={
            engaged
              ? "rounded border border-red-700 bg-red-600 px-3 py-1 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50"
              : "rounded border border-amber-600 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-950 hover:bg-amber-100 disabled:opacity-50"
          }
          title={
            authed
              ? "L1 emergency pause — always visible; confirm before change"
              : "Log in to control L1 pause"
          }
          aria-pressed={engaged}
        >
          L1 {engaged ? "ENGAGED" : "Pause"}
          {busy ? "…" : ""}
        </button>

        <div className="flex gap-2" aria-label="Higher kill-switch levels (not In-MVP)">
          {HIGHER_LEVELS.map((level) => (
            <button
              key={level}
              type="button"
              disabled
              className="rounded border border-neutral-300 bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-400"
              title="L2–L4 not In-MVP for this stub contract"
            >
              {level}
            </button>
          ))}
        </div>

        <div className="ml-auto flex flex-wrap items-center gap-3 text-xs text-neutral-600">
          {status ? (
            <span>
              Status:{" "}
              <strong className="font-medium text-neutral-900">
                {engaged ? "paused" : "open"}
              </strong>
              {status.reason ? ` — ${status.reason}` : ""}
            </span>
          ) : null}
          <Link
            href="/alerts"
            className="underline hover:text-neutral-900"
          >
            Alerts
          </Link>
        </div>
      </div>

      {message ? (
        <div
          role="status"
          className={
            messageKind === "stub"
              ? "border-t border-amber-200 bg-amber-50 px-4 py-1.5 text-xs text-amber-950"
              : messageKind === "err"
                ? "border-t border-red-200 bg-red-50 px-4 py-1.5 text-xs text-red-900"
                : "border-t border-neutral-100 bg-neutral-50 px-4 py-1.5 text-xs text-neutral-700"
          }
        >
          <span className="mx-auto block max-w-5xl">{message}</span>
        </div>
      ) : null}
    </header>
  );
}
