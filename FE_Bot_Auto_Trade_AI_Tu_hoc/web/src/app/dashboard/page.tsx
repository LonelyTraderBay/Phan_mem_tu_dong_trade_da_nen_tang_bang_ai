"use client";

import { useCallback, useEffect, useState } from "react";
import { AccountIdInput } from "@/components/AccountIdInput";
import { RequireAuth } from "@/components/RequireAuth";
import { getStoredAccountId } from "@/lib/api/auth-storage";
import { getPnlSummary, getPositions, getReportsTrades } from "@/lib/api/client";
import type { PnlSummary, Position, TradeReport } from "@/lib/api/types";
import { ApiErrorBanner, EmptyState } from "@/lib/api/ui";

function DashboardInner() {
  const [accountId, setAccountId] = useState("");
  const [positions, setPositions] = useState<Position[]>([]);
  const [pnl, setPnl] = useState<PnlSummary | null>(null);
  const [trades, setTrades] = useState<TradeReport[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (id: string) => {
    if (!id.trim()) {
      setPositions([]);
      setPnl(null);
      setTrades([]);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const [posRes, pnlRes, tradeRes] = await Promise.all([
        getPositions({ account_id: id.trim(), open_only: true }),
        getPnlSummary({ account_id: id.trim() }),
        getReportsTrades({ account_id: id.trim(), limit: 20 }),
      ]);
      // Display server numbers only — do not recompute PnL client-side as truth
      setPositions(posRes.data);
      setPnl(pnlRes.data);
      setTrades(tradeRes.data);
    } catch (err) {
      setPositions([]);
      setPnl(null);
      setTrades([]);
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
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Positions, PnL summary, and recent trades — server values only (display-only).
        </p>
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

      <section className="rounded border border-neutral-200 bg-white p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
          PnL summary (server)
        </h2>
        {pnl ? (
          <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-neutral-500">Currency</dt>
              <dd className="font-mono">{pnl.currency}</dd>
            </div>
            <div>
              <dt className="text-neutral-500">Calculated at</dt>
              <dd className="font-mono text-xs">{pnl.calculated_at}</dd>
            </div>
            <div>
              <dt className="text-neutral-500">Realized</dt>
              <dd className="font-mono">{pnl.realized_pnl}</dd>
            </div>
            <div>
              <dt className="text-neutral-500">Unrealized</dt>
              <dd className="font-mono">{pnl.unrealized_pnl}</dd>
            </div>
            <div>
              <dt className="text-neutral-500">Total</dt>
              <dd className="font-mono font-semibold">{pnl.total_pnl}</dd>
            </div>
            {pnl.trade_count !== undefined ? (
              <div>
                <dt className="text-neutral-500">Trade count</dt>
                <dd className="font-mono">{pnl.trade_count}</dd>
              </div>
            ) : null}
          </dl>
        ) : (
          <EmptyState>No PnL summary loaded.</EmptyState>
        )}
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Positions
        </h2>
        {positions.length === 0 ? (
          <EmptyState>No open positions.</EmptyState>
        ) : (
          <div className="mt-2 overflow-x-auto rounded border border-neutral-200 bg-white">
            <table className="min-w-full text-left text-xs">
              <thead className="border-b bg-neutral-50 text-neutral-600">
                <tr>
                  <th className="px-2 py-2">Symbol</th>
                  <th className="px-2 py-2">Side</th>
                  <th className="px-2 py-2">Qty</th>
                  <th className="px-2 py-2">Entry</th>
                  <th className="px-2 py-2">Mark</th>
                  <th className="px-2 py-2">uPnL (server)</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => (
                  <tr key={p.id} className="border-b border-neutral-100">
                    <td className="px-2 py-1 font-mono">{p.symbol}</td>
                    <td className="px-2 py-1">{p.side}</td>
                    <td className="px-2 py-1">{p.quantity}</td>
                    <td className="px-2 py-1">{p.entry_price}</td>
                    <td className="px-2 py-1">{p.mark_price ?? "—"}</td>
                    <td className="px-2 py-1">{p.unrealized_pnl ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Recent activity (trades)
        </h2>
        {trades.length === 0 ? (
          <EmptyState>No recent trades.</EmptyState>
        ) : (
          <div className="mt-2 overflow-x-auto rounded border border-neutral-200 bg-white">
            <table className="min-w-full text-left text-xs">
              <thead className="border-b bg-neutral-50 text-neutral-600">
                <tr>
                  <th className="px-2 py-2">Time</th>
                  <th className="px-2 py-2">Symbol</th>
                  <th className="px-2 py-2">Side</th>
                  <th className="px-2 py-2">Qty</th>
                  <th className="px-2 py-2">Price</th>
                  <th className="px-2 py-2">rPnL (server)</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((t) => (
                  <tr key={t.trade_id} className="border-b border-neutral-100">
                    <td className="px-2 py-1 font-mono">{t.executed_at}</td>
                    <td className="px-2 py-1 font-mono">{t.symbol}</td>
                    <td className="px-2 py-1">{t.side}</td>
                    <td className="px-2 py-1">{t.quantity}</td>
                    <td className="px-2 py-1">{t.price}</td>
                    <td className="px-2 py-1">{t.realized_pnl ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardInner />
    </RequireAuth>
  );
}
