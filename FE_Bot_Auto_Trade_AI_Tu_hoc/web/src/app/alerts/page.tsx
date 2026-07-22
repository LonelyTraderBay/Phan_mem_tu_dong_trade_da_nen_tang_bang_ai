"use client";

import { useCallback, useEffect, useState } from "react";
import { AccountIdInput } from "@/components/AccountIdInput";
import { RequireAuth } from "@/components/RequireAuth";
import { getStoredAccountId } from "@/lib/api/auth-storage";
import { getAlerts } from "@/lib/api/client";
import type { Alert } from "@/lib/api/types";
import { ApiErrorBanner, EmptyState } from "@/lib/api/ui";

function AlertsInner() {
  const [accountId, setAccountId] = useState("");
  const [items, setItems] = useState<Alert[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (id: string) => {
    if (!id.trim()) {
      setItems([]);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await getAlerts({ account_id: id.trim(), limit: 50 });
      setItems(res.data);
    } catch (err) {
      setItems([]);
      setError(err);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    const id = getStoredAccountId();
    setAccountId(id);
    if (id) void load(id);
  }, [load]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Alerts</h1>
        <p className="mt-1 text-sm text-neutral-600">Inbox from getAlerts.</p>
      </div>

      <AccountIdInput
        value={accountId}
        onChange={(id) => {
          setAccountId(id);
          void load(id);
        }}
      />

      <button
        type="button"
        disabled={busy || !accountId}
        onClick={() => void load(accountId)}
        className="rounded border border-neutral-300 px-3 py-1.5 text-sm disabled:opacity-50"
      >
        Refresh
      </button>

      {error ? <ApiErrorBanner error={error} /> : null}

      {items.length === 0 ? (
        <EmptyState>No alerts.</EmptyState>
      ) : (
        <ul className="divide-y divide-neutral-200 rounded border border-neutral-200 bg-white">
          {items.map((a) => (
            <li key={a.id} className="px-3 py-3 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded px-1.5 py-0.5 text-xs font-medium uppercase ${
                    a.severity === "critical"
                      ? "bg-red-100 text-red-800"
                      : a.severity === "warning"
                        ? "bg-amber-100 text-amber-900"
                        : "bg-neutral-100 text-neutral-700"
                  }`}
                >
                  {a.severity}
                </span>
                <span className="font-mono text-xs text-neutral-500">{a.code}</span>
                {a.acknowledged ? (
                  <span className="text-xs text-neutral-400">acked</span>
                ) : (
                  <span className="text-xs text-neutral-700">unacked</span>
                )}
              </div>
              <p className="mt-1">{a.message}</p>
              <p className="mt-0.5 font-mono text-xs text-neutral-400">{a.created_at}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function AlertsPage() {
  return (
    <RequireAuth>
      <AlertsInner />
    </RequireAuth>
  );
}
