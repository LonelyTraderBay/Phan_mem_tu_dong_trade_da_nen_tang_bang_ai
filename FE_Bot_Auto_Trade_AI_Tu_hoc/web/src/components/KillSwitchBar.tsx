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
 * Mutate only after window.confirm. L2–L4 disabled (not In-MVP contract shape).
 */
export function KillSwitchBar() {
  const router = useRouter();
  const [status, setStatus] = useState<KillSwitchStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [stub, setStub] = useState(false);
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
      setStub(result.kind === "stub_not_implemented");
      setMessage(formatApiFailureForUi(result));
      if (result.kind === "unauthorized") {
        setAuthed(false);
        router.replace("/login");
      }
      return;
    }
    setStub(false);
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
      setMessage("Reason is required to change kill-switch.");
      return;
    }

    setBusy(true);
    setMessage(null);
    const result = await postKillSwitch({
      engaged: nextEngaged,
      reason: trimmed.slice(0, 500),
    });
    setBusy(false);

    if (!result.ok) {
      setStub(result.kind === "stub_not_implemented");
      setMessage(formatApiFailureForUi(result));
      if (result.kind === "unauthorized") {
        setAuthed(false);
        router.replace("/login");
      }
      return;
    }

    setStub(false);
    setStatus(result.data);
    setMessage(
      result.data.engaged
        ? "L1 engaged — new entries paused."
        : "L1 disengaged — new entries allowed (subject to risk).",
    );
  }

  const engaged = status?.engaged === true;

  return (
    <header className="border-b border-neutral-200 bg-white">
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
            stub
              ? "border-t border-amber-200 bg-amber-50 px-4 py-1.5 text-xs text-amber-950"
              : "border-t border-neutral-100 bg-neutral-50 px-4 py-1.5 text-xs text-neutral-700"
          }
        >
          <span className="mx-auto block max-w-5xl">{message}</span>
        </div>
      ) : null}
    </header>
  );
}
