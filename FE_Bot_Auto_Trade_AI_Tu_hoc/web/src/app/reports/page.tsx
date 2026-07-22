"use client";

import { useEffect, useState, type FormEvent } from "react";
import { AccountIdInput } from "@/components/AccountIdInput";
import { RequireAuth } from "@/components/RequireAuth";
import { getStoredAccountId } from "@/lib/api/auth-storage";
import { getReportsTrades } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";
import type { TradeReport } from "@/lib/api/types";
import { ApiErrorBanner, EmptyState } from "@/lib/api/ui";

function buildSummaryText(trades: TradeReport[], accountId: string): string {
  const lines = [
    `Trade report summary`,
    `account_id: ${accountId}`,
    `count: ${trades.length}`,
    `generated_at: ${new Date().toISOString()}`,
    "",
    ...trades.map(
      (t) =>
        `${t.executed_at}\t${t.symbol}\t${t.side}\t${t.quantity}\t${t.price}\trPnL=${t.realized_pnl ?? "n/a"}\tid=${t.trade_id}`,
    ),
  ];
  return lines.join("\n");
}

function ReportsInner() {
  const [accountId, setAccountId] = useState("");
  const [strategyId, setStrategyId] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [trades, setTrades] = useState<TradeReport[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [copyMsg, setCopyMsg] = useState("");

  useEffect(() => {
    setAccountId(getStoredAccountId());
  }, []);

  async function onFilter(e: FormEvent) {
    e.preventDefault();
    if (!accountId.trim()) {
      setError(new Error("Account ID required"));
      return;
    }
    setBusy(true);
    setError(null);
    setCopyMsg("");
    try {
      const res = await getReportsTrades({
        account_id: accountId.trim(),
        strategy_id: strategyId.trim() || undefined,
        from: from || undefined,
        to: to || undefined,
        limit: 100,
      });
      setTrades(res.data);
    } catch (err) {
      setTrades([]);
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function copySummary() {
    const text = buildSummaryText(trades, accountId.trim());
    try {
      await navigator.clipboard.writeText(text);
      setCopyMsg("Copied summary to clipboard.");
    } catch {
      setCopyMsg("Clipboard unavailable — select text from export box below.");
    }
  }

  function downloadSummary() {
    const text = buildSummaryText(trades, accountId.trim());
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `trades-${accountId.trim() || "report"}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const is501 = error instanceof ApiError && error.isNotImplemented;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Reports</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Filter trades and copy/export summary text. Server numbers only.
        </p>
      </div>

      <form onSubmit={onFilter} className="space-y-3 rounded border border-neutral-200 bg-white p-4">
        <AccountIdInput value={accountId} onChange={setAccountId} />
        <label className="block text-sm">
          <span className="font-medium">Strategy ID (optional)</span>
          <input
            value={strategyId}
            onChange={(e) => setStrategyId(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 font-mono text-sm"
          />
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-sm">
            <span className="font-medium">From (ISO)</span>
            <input
              type="datetime-local"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium">To (ISO)</span>
            <input
              type="datetime-local"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
            />
          </label>
        </div>
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-neutral-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {busy ? "Loading…" : "Apply filter"}
        </button>
      </form>

      {error ? <ApiErrorBanner error={error} /> : null}
      {is501 ? (
        <EmptyState>
          Reports endpoint returned 501 Not Implemented — empty result, no invented trades.
        </EmptyState>
      ) : null}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={trades.length === 0}
          onClick={() => void copySummary()}
          className="rounded border border-neutral-300 px-3 py-1.5 text-sm disabled:opacity-50"
        >
          Copy summary
        </button>
        <button
          type="button"
          disabled={trades.length === 0}
          onClick={downloadSummary}
          className="rounded border border-neutral-300 px-3 py-1.5 text-sm disabled:opacity-50"
        >
          Export .txt
        </button>
        {copyMsg ? <span className="text-sm text-neutral-600">{copyMsg}</span> : null}
      </div>

      {trades.length === 0 && !error ? (
        <EmptyState>No trades for this filter.</EmptyState>
      ) : null}

      {trades.length > 0 ? (
        <div className="overflow-x-auto rounded border border-neutral-200 bg-white">
          <table className="min-w-full text-left text-xs">
            <thead className="border-b bg-neutral-50 text-neutral-600">
              <tr>
                <th className="px-2 py-2">Time</th>
                <th className="px-2 py-2">Symbol</th>
                <th className="px-2 py-2">Side</th>
                <th className="px-2 py-2">Qty</th>
                <th className="px-2 py-2">Price</th>
                <th className="px-2 py-2">Fee</th>
                <th className="px-2 py-2">rPnL</th>
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
                  <td className="px-2 py-1">
                    {t.fee ?? "—"}
                    {t.fee_currency ? ` ${t.fee_currency}` : ""}
                  </td>
                  <td className="px-2 py-1">{t.realized_pnl ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {trades.length > 0 ? (
        <textarea
          readOnly
          className="h-40 w-full rounded border border-neutral-200 bg-neutral-50 p-2 font-mono text-xs"
          value={buildSummaryText(trades, accountId.trim())}
        />
      ) : null}
    </div>
  );
}

export default function ReportsPage() {
  return (
    <RequireAuth>
      <ReportsInner />
    </RequireAuth>
  );
}
