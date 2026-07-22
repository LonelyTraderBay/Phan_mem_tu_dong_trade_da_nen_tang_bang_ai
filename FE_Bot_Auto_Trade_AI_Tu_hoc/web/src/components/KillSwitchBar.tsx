"use client";

import { useCallback, useEffect, useState } from "react";
import { isAuthenticated } from "@/lib/api/auth-storage";
import { getKillSwitchStatus, postKillSwitch } from "@/lib/api/client";
import type { KillSwitchStatus } from "@/lib/api/types";
import { ApiErrorBanner } from "@/lib/api/ui";

/**
 * L1 emergency pause — always visible in layout (In-MVP).
 * L2–L4 remain disabled stubs (higher levels / SoD out of this paper stub).
 * Wire: getKillSwitchStatus / postKillSwitch (engaged + reason only in OpenAPI).
 */
export function KillSwitchBar() {
  const [status, setStatus] = useState<KillSwitchStatus | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [authed, setAuthed] = useState(false);

  const refresh = useCallback(async () => {
    const ok = isAuthenticated();
    setAuthed(ok);
    if (!ok) {
      setStatus(null);
      return;
    }
    try {
      setError(null);
      const res = await getKillSwitchStatus();
      setStatus(res.data);
    } catch (err) {
      setError(err);
      setStatus(null);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), 15_000);
    const onFocus = () => void refresh();
    window.addEventListener("focus", onFocus);
    return () => {
      window.clearInterval(id);
      window.removeEventListener("focus", onFocus);
    };
  }, [refresh]);

  async function toggle(engaged: boolean) {
    const action = engaged ? "ENGAGE L1 (pause new entries)" : "DISENGAGE L1";
    const reasonDefault = engaged ? "operator L1 engage" : "operator L1 disengage";
    if (!window.confirm(`Confirm ${action}?`)) return;
    const reason = window.prompt("Reason (required)", reasonDefault);
    if (!reason || !reason.trim()) return;

    setBusy(true);
    setError(null);
    try {
      const res = await postKillSwitch({ engaged, reason: reason.trim() });
      setStatus(res.data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
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
          disabled={busy || !authed}
          onClick={() => void toggle(!engaged)}
          className={`rounded border px-3 py-1 text-xs font-medium disabled:opacity-50 ${
            engaged
              ? "border-red-600 bg-red-600 text-white"
              : "border-neutral-800 bg-neutral-800 text-white hover:bg-neutral-700"
          }`}
          title="L1 pause new entries — always visible"
        >
          L1 {engaged ? "ENGAGED" : "disengaged"}
        </button>
        <button
          type="button"
          disabled
          className="rounded border border-neutral-300 bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-400"
          title="Out of MVP paper stub"
        >
          L2 (deferred)
        </button>
        <button
          type="button"
          disabled
          className="rounded border border-neutral-300 bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-400"
          title="Out of MVP paper stub"
        >
          L3 (deferred)
        </button>
        <button
          type="button"
          disabled
          className="rounded border border-neutral-300 bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-400"
          title="Out of MVP paper stub"
        >
          L4 (deferred)
        </button>
        {status ? (
          <span className="text-xs text-neutral-500">
            updated {status.updated_at}
            {status.reason ? ` · ${status.reason}` : ""}
          </span>
        ) : (
          <span className="text-xs text-neutral-400">
            {authed ? "status unknown" : "login to control L1"}
          </span>
        )}
      </div>
      {error ? (
        <div className="mx-auto max-w-5xl px-4 pb-2">
          <ApiErrorBanner error={error} />
        </div>
      ) : null}
    </header>
  );
}
