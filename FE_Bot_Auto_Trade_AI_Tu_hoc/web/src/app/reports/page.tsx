"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import type { ApiFailure } from "@/lib/api/client";
import { hasAccessToken } from "@/lib/auth/tokenStore";
import {
  formatApiFailureForUi,
  listTradeReports,
} from "@/lib/portfolio/api";
import type { TradeReport } from "@/lib/portfolio/types";

type MessageKind = "ok" | "err" | "stub";

/**
 * Reports / history-review — getReportsTrades.
 * Filter + list + copy/export summary text. Display server fields only.
 */
export default function ReportsPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  const [accountId, setAccountId] = useState("");
  const [strategyId, setStrategyId] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [limit, setLimit] = useState("100");

  const [trades, setTrades] = useState<TradeReport[]>([]);
  const [busy, setBusy] = useState(false);
  const [messageKind, setMessageKind] = useState<MessageKind | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);

  const handleFailure = useCallback(
    (result: ApiFailure) => {
      setTrades([]);
      setMessageKind(result.kind === "stub_not_implemented" ? "stub" : "err");
      setMessage(
        result.kind === "stub_not_implemented"
          ? `${formatApiFailureForUi(result)} — endpoint chưa sẵn sàng.`
          : formatApiFailureForUi(result),
      );
      if (result.kind === "unauthorized") {
        router.replace("/login");
      }
    },
    [router],
  );

  const loadTrades = useCallback(async () => {
    const account = accountId.trim();
    if (!account) {
      setTrades([]);
      setMessageKind("err");
      setMessage("Cần account_id (OpenAPI bắt buộc cho getReportsTrades).");
      return;
    }

    setBusy(true);
    setMessage(null);
    setMessageKind(null);
    setCopyStatus(null);

    const parsedLimit = Number.parseInt(limit, 10);
    const result = await listTradeReports({
      accountId: account,
      ...(strategyId.trim() ? { strategyId: strategyId.trim() } : {}),
      ...(from.trim() ? { from: toIsoOrRaw(from.trim()) } : {}),
      ...(to.trim() ? { to: toIsoOrRaw(to.trim()) } : {}),
      ...(Number.isFinite(parsedLimit) && parsedLimit >= 1
        ? { limit: Math.min(parsedLimit, 500) }
        : { limit: 100 }),
    });

    setBusy(false);

    if (!result.ok) {
      handleFailure(result);
      return;
    }

    setTrades(result.data);
    setMessageKind("ok");
    setMessage(
      result.data.length === 0
        ? "Không có trade (empty list từ server)."
        : `${result.data.length} trade(s) từ getReportsTrades.`,
    );
  }, [accountId, from, handleFailure, limit, strategyId, to]);

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  function applyTodayFilter() {
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    const end = new Date();
    end.setHours(23, 59, 59, 999);
    setFrom(toDatetimeLocalValue(start));
    setTo(toDatetimeLocalValue(end));
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    await loadTrades();
  }

  async function onCopySummary() {
    const text = buildTradeSummaryText({
      accountId: accountId.trim(),
      strategyId: strategyId.trim() || null,
      from: from.trim() || null,
      to: to.trim() || null,
      trades,
    });
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus("Đã copy summary vào clipboard.");
    } catch {
      setCopyStatus("Không copy được clipboard — dùng Export để tải file.");
    }
  }

  function onExportSummary() {
    const text = buildTradeSummaryText({
      accountId: accountId.trim(),
      strategyId: strategyId.trim() || null,
      from: from.trim() || null,
      to: to.trim() || null,
      trades,
    });
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `trade-history-${stampForFilename()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setCopyStatus("Đã tải file summary (.txt).");
  }

  if (!ready) {
    return (
      <p className="text-sm text-neutral-600">Đang kiểm tra phiên…</p>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-2xl font-semibold tracking-tight">Reports</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Trade history review — lọc và list từ getReportsTrades. Copy/export
        summary text (server fields only; không tính PnL client).
      </p>

      <p className="mt-3 text-sm">
        <Link
          href="/"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          ← Screens
        </Link>
        {" · "}
        <Link
          href="/dashboard"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          Dashboard
        </Link>
        {" · "}
        <Link
          href="/login"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          Login
        </Link>
      </p>

      <form
        onSubmit={onSubmit}
        className="mt-6 grid gap-3 sm:grid-cols-2"
      >
        <div className="sm:col-span-2">
          <label htmlFor="reports-account-id" className="block text-sm font-medium">
            Account ID
          </label>
          <input
            id="reports-account-id"
            name="account_id"
            type="text"
            required
            value={accountId}
            onChange={(ev) => setAccountId(ev.target.value)}
            placeholder="uuid"
            className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 font-mono text-xs outline-none focus:border-neutral-500"
          />
        </div>

        <div>
          <label htmlFor="reports-strategy-id" className="block text-sm font-medium">
            Strategy ID (optional)
          </label>
          <input
            id="reports-strategy-id"
            name="strategy_id"
            type="text"
            value={strategyId}
            onChange={(ev) => setStrategyId(ev.target.value)}
            placeholder="uuid"
            className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 font-mono text-xs outline-none focus:border-neutral-500"
          />
        </div>

        <div>
          <label htmlFor="reports-limit" className="block text-sm font-medium">
            Limit (1–500)
          </label>
          <input
            id="reports-limit"
            name="limit"
            type="number"
            min={1}
            max={500}
            value={limit}
            onChange={(ev) => setLimit(ev.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
          />
        </div>

        <div>
          <label htmlFor="reports-from" className="block text-sm font-medium">
            From
          </label>
          <input
            id="reports-from"
            name="from"
            type="datetime-local"
            value={from}
            onChange={(ev) => setFrom(ev.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
          />
        </div>

        <div>
          <label htmlFor="reports-to" className="block text-sm font-medium">
            To
          </label>
          <input
            id="reports-to"
            name="to"
            type="datetime-local"
            value={to}
            onChange={(ev) => setTo(ev.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
          />
        </div>

        <div className="flex flex-wrap items-end gap-2 sm:col-span-2">
          <button
            type="button"
            onClick={applyTodayFilter}
            disabled={busy}
            className="rounded border border-neutral-300 bg-white px-3 py-2 text-sm hover:bg-neutral-50 disabled:opacity-50"
          >
            Today
          </button>
          <button
            type="submit"
            disabled={busy}
            className="rounded border border-neutral-800 bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
          >
            {busy ? "Đang tải…" : "Tải lịch sử"}
          </button>
          <button
            type="button"
            onClick={() => void onCopySummary()}
            disabled={busy || trades.length === 0}
            className="rounded border border-neutral-300 bg-white px-3 py-2 text-sm hover:bg-neutral-50 disabled:opacity-50"
          >
            Copy summary
          </button>
          <button
            type="button"
            onClick={onExportSummary}
            disabled={busy || trades.length === 0}
            className="rounded border border-neutral-300 bg-white px-3 py-2 text-sm hover:bg-neutral-50 disabled:opacity-50"
          >
            Export .txt
          </button>
        </div>
      </form>

      {message ? (
        <div
          role="alert"
          className={
            messageKind === "ok"
              ? "mt-4 rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900"
              : messageKind === "stub"
                ? "mt-4 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950"
                : "mt-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900"
          }
        >
          {message}
        </div>
      ) : null}

      {copyStatus ? (
        <p className="mt-2 text-sm text-neutral-600" role="status">
          {copyStatus}
        </p>
      ) : null}

      <section className="mt-8">
        <h2 className="text-lg font-medium">Trade history</h2>
        {trades.length === 0 ? (
          <p className="mt-2 text-sm text-neutral-600">
            Không có trade — API fail / 501 / empty. UI không bịa số liệu.
          </p>
        ) : (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[44rem] border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-neutral-300 text-neutral-600">
                  <th className="py-2 pr-3 font-medium">executed_at</th>
                  <th className="py-2 pr-3 font-medium">symbol</th>
                  <th className="py-2 pr-3 font-medium">side</th>
                  <th className="py-2 pr-3 font-medium">quantity</th>
                  <th className="py-2 pr-3 font-medium">price</th>
                  <th className="py-2 pr-3 font-medium">fee</th>
                  <th className="py-2 pr-3 font-medium">realized_pnl</th>
                  <th className="py-2 font-medium">trade_id</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((t) => (
                  <tr
                    key={t.trade_id}
                    className="border-b border-neutral-100 font-mono"
                  >
                    <td className="py-1.5 pr-3">{t.executed_at}</td>
                    <td className="py-1.5 pr-3">{t.symbol}</td>
                    <td className="py-1.5 pr-3">{t.side}</td>
                    <td className="py-1.5 pr-3">{t.quantity}</td>
                    <td className="py-1.5 pr-3">{t.price}</td>
                    <td className="py-1.5 pr-3">
                      {t.fee !== undefined
                        ? `${t.fee}${t.fee_currency ? ` ${t.fee_currency}` : ""}`
                        : "—"}
                    </td>
                    <td className="py-1.5 pr-3">
                      {t.realized_pnl !== undefined ? t.realized_pnl : "—"}
                    </td>
                    <td className="py-1.5">{t.trade_id}</td>
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

function toDatetimeLocalValue(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** datetime-local → ISO; already-ISO strings pass through. */
function toIsoOrRaw(value: string): string {
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value)) {
    const d = new Date(value);
    if (!Number.isNaN(d.getTime())) return d.toISOString();
  }
  return value;
}

function stampForFilename(): string {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function buildTradeSummaryText(options: {
  accountId: string;
  strategyId: string | null;
  from: string | null;
  to: string | null;
  trades: TradeReport[];
}): string {
  const lines: string[] = [
    "Trade history summary (getReportsTrades — server fields)",
    `generated_at: ${new Date().toISOString()}`,
    `account_id: ${options.accountId || "(none)"}`,
    `strategy_id: ${options.strategyId ?? "(any)"}`,
    `from: ${options.from ?? "(none)"}`,
    `to: ${options.to ?? "(none)"}`,
    `trade_count: ${options.trades.length}`,
    "",
    "trades:",
  ];

  if (options.trades.length === 0) {
    lines.push("(empty)");
  } else {
    for (const t of options.trades) {
      const parts = [
        t.executed_at,
        t.symbol,
        t.side,
        `qty=${t.quantity}`,
        `price=${t.price}`,
        t.fee !== undefined
          ? `fee=${t.fee}${t.fee_currency ? ` ${t.fee_currency}` : ""}`
          : null,
        t.realized_pnl !== undefined ? `realized_pnl=${t.realized_pnl}` : null,
        t.strategy_id ? `strategy_id=${t.strategy_id}` : null,
        `trade_id=${t.trade_id}`,
      ].filter((p): p is string => p !== null);
      lines.push(`- ${parts.join(" | ")}`);
    }
  }

  return `${lines.join("\n")}\n`;
}
