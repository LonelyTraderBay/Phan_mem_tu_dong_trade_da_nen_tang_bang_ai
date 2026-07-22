"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { AccountIdInput } from "@/components/AccountIdInput";
import { RequireAuth } from "@/components/RequireAuth";
import { getStoredAccountId } from "@/lib/api/auth-storage";
import { getStrategies, patchStrategy, postStrategies } from "@/lib/api/client";
import type { CandleInterval, Strategy, StrategyStatus } from "@/lib/api/types";
import { ApiErrorBanner, EmptyState } from "@/lib/api/ui";

const TIMEFRAMES: CandleInterval[] = ["1m", "5m", "15m", "1h", "4h", "1d"];

function StrategiesInner() {
  const [accountId, setAccountId] = useState("");
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [timeframe, setTimeframe] = useState<CandleInterval>("15m");
  const [items, setItems] = useState<Strategy[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  const load = useCallback(async (id: string) => {
    if (!id.trim()) {
      setItems([]);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await getStrategies({ account_id: id.trim() });
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

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    if (!accountId.trim()) {
      setError(new Error("Account ID required"));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await postStrategies({
        account_id: accountId.trim(),
        name: name.trim(),
        symbol: symbol.trim(),
        timeframe,
        status: "draft",
      });
      setName("");
      await load(accountId);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function setStatus(strategy: Strategy, status: StrategyStatus) {
    setBusy(true);
    setError(null);
    try {
      await patchStrategy(strategy.id, { status });
      await load(accountId);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Strategies</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Form-based create and start/stop/pause. No no-code builder in MVP.
        </p>
      </div>

      {error ? <ApiErrorBanner error={error} /> : null}

      <AccountIdInput
        value={accountId}
        onChange={(id) => {
          setAccountId(id);
          void load(id);
        }}
      />

      <form onSubmit={onCreate} className="space-y-3 rounded border border-neutral-200 bg-white p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Create strategy
        </h2>
        <label className="block text-sm">
          <span className="font-medium">Name</span>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">Symbol</span>
          <input
            required
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">Timeframe</span>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as CandleInterval)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
          >
            {TIMEFRAMES.map((tf) => (
              <option key={tf} value={tf}>
                {tf}
              </option>
            ))}
          </select>
        </label>
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-neutral-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Create
        </button>
      </form>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
            List
          </h2>
          <button
            type="button"
            disabled={busy || !accountId}
            onClick={() => void load(accountId)}
            className="text-xs text-neutral-600 underline disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
        {items.length === 0 ? (
          <EmptyState>No strategies (or API returned empty / error).</EmptyState>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded border border-neutral-200 bg-white">
            {items.map((s) => (
              <li key={s.id} className="flex flex-wrap items-center gap-2 px-3 py-3 text-sm">
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{s.name}</p>
                  <p className="font-mono text-xs text-neutral-500">
                    {s.symbol} · {s.timeframe} · {s.status}
                  </p>
                </div>
                <button
                  type="button"
                  disabled={busy || s.status === "active"}
                  onClick={() => void setStatus(s, "active")}
                  className="rounded border border-neutral-300 px-2 py-1 text-xs disabled:opacity-40"
                >
                  Start
                </button>
                <button
                  type="button"
                  disabled={busy || s.status === "paused"}
                  onClick={() => void setStatus(s, "paused")}
                  className="rounded border border-neutral-300 px-2 py-1 text-xs disabled:opacity-40"
                >
                  Pause
                </button>
                <button
                  type="button"
                  disabled={busy || s.status === "stopped"}
                  onClick={() => void setStatus(s, "stopped")}
                  className="rounded border border-neutral-300 px-2 py-1 text-xs disabled:opacity-40"
                >
                  Stop
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function StrategiesPage() {
  return (
    <RequireAuth>
      <StrategiesInner />
    </RequireAuth>
  );
}
