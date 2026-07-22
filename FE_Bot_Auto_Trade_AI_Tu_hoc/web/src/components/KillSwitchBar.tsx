"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  formatApiFailureForUi,
  getKillSwitchStatus,
  postKillSwitch,
} from "@/lib/kill-switch/api";
import type {
  KillSwitchLevel,
  KillSwitchStatus,
} from "@/lib/kill-switch/types";
import { hasAccessToken } from "@/lib/auth/tokenStore";

const LEVELS: KillSwitchLevel[] = ["L1", "L2", "L3", "L4"];

/**
 * Always-visible kill-switch (layout header).
 * L1: confirm + reason. L2–L4: confirm + confirmed=true + reason (RFC-0002).
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

  async function mutate(next: {
    engaged: boolean;
    level?: KillSwitchLevel;
    needsConfirmed: boolean;
    label: string;
  }) {
    if (busy) return;
    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }

    const confirmedUi = window.confirm(
      `${next.label}\n\nThis calls postKillSwitch.`,
    );
    if (!confirmedUi) return;

    const reason = window.prompt(
      "Reason (required):",
      next.engaged
        ? `Operator ${next.level ?? "L1"} engage`
        : "Operator resume",
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
      engaged: next.engaged,
      reason: trimmed.slice(0, 500),
      ...(next.level ? { level: next.level } : {}),
      ...(next.needsConfirmed ? { confirmed: true } : {}),
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
        ? `${result.data.level ?? "L1"} engaged — protective mode (server).`
        : "Kill-switch cleared — entries subject to risk (server).",
    );
  }

  const engaged = status?.engaged === true;
  const activeLevel = status?.level ?? null;

  return (
    <header className="border-b border-neutral-200 bg-white">
      {engaged ? (
        <div
          role="status"
          className="border-b border-red-700 bg-red-600 px-4 py-1 text-center text-xs font-semibold text-white"
        >
          {activeLevel ?? "L1"} ENGAGED — protective mode (from API)
          {status?.updated_at ? ` · updated_at ${status.updated_at}` : ""}
        </div>
      ) : null}
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3 px-4 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Kill switch
        </span>

        {LEVELS.map((level) => {
          const isActive = engaged && activeLevel === level;
          const needsConfirmed = level !== "L1";
          return (
            <button
              key={level}
              type="button"
              onClick={() =>
                void mutate({
                  engaged: true,
                  level,
                  needsConfirmed,
                  label: `Engage kill-switch ${level} (paper/staging)`,
                })
              }
              disabled={busy || !authed}
              className={
                isActive
                  ? "rounded border border-red-700 bg-red-600 px-3 py-1 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50"
                  : "rounded border border-amber-600 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-950 hover:bg-amber-100 disabled:opacity-50"
              }
              title={
                authed
                  ? needsConfirmed
                    ? `${level} requires UI confirm + confirmed=true`
                    : "L1 emergency pause"
                  : "Log in to control kill-switch"
              }
              aria-pressed={isActive}
            >
              {level}
              {isActive ? " ON" : ""}
              {busy ? "…" : ""}
            </button>
          );
        })}

        <button
          type="button"
          onClick={() =>
            void mutate({
              engaged: false,
              needsConfirmed: Boolean(
                activeLevel && activeLevel !== "L1",
              ),
              label: "Clear / disengage kill-switch",
            })
          }
          disabled={busy || !authed || !engaged}
          className="rounded border border-neutral-400 bg-white px-3 py-1 text-xs font-medium text-neutral-800 hover:bg-neutral-50 disabled:opacity-50"
        >
          Clear
        </button>

        <div className="ml-auto flex flex-wrap items-center gap-3 text-xs text-neutral-600">
          {status ? (
            <span>
              Status:{" "}
              <strong className="font-medium text-neutral-900">
                {engaged ? activeLevel ?? "paused" : "open"}
              </strong>
              {status.reason ? ` — ${status.reason}` : ""}
            </span>
          ) : null}
          <Link href="/alerts" className="underline hover:text-neutral-900">
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
