"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import type { ApiFailure } from "@/lib/api/client";
import { hasAccessToken } from "@/lib/auth/tokenStore";
import {
  formatApiFailureForUi,
  getPnlSummary,
  listPositions,
  listTradeReports,
} from "@/lib/portfolio/api";
import type { PnlSummary, Position, TradeReport } from "@/lib/portfolio/types";

type MessageKind = "ok" | "err" | "stub";

type SectionStatus = {
  kind: MessageKind | null;
  message: string | null;
};

/**
 * Dashboard — getPositions / getPnlSummary / getReportsTrades.
 * Display-only: show server fields; never compute PnL client-side as truth.
 */
export default function DashboardPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  const [accountId, setAccountId] = useState("");
  const [positions, setPositions] = useState<Position[]>([]);
  const [pnl, setPnl] = useState<PnlSummary | null>(null);
  const [trades, setTrades] = useState<TradeReport[]>([]);

  const [busy, setBusy] = useState(false);
  const [positionsStatus, setPositionsStatus] = useState<SectionStatus>({
    kind: null,
    message: null,
  });
  const [pnlStatus, setPnlStatus] = useState<SectionStatus>({
    kind: null,
    message: null,
  });
  const [activityStatus, setActivityStatus] = useState<SectionStatus>({
    kind: null,
    message: null,
  });

  const handleFailure = useCallback(
    (
      result: ApiFailure,
      setStatus: (s: SectionStatus) => void,
      clear: () => void,
    ) => {
      clear();
      setStatus({
        kind: result.kind === "stub_not_implemented" ? "stub" : "err",
        message:
          result.kind === "stub_not_implemented"
            ? `${formatApiFailureForUi(result)} — endpoint chưa sẵn sàng.`
            : formatApiFailureForUi(result),
      });
      if (result.kind === "unauthorized") {
        router.replace("/login");
      }
    },
    [router],
  );

  const loadAll = useCallback(
    async (account: string) => {
      setBusy(true);
      setPositionsStatus({ kind: null, message: null });
      setPnlStatus({ kind: null, message: null });
      setActivityStatus({ kind: null, message: null });

      const [posResult, pnlResult, tradesResult] = await Promise.all([
        listPositions({ accountId: account, openOnly: true }),
        getPnlSummary({ accountId: account }),
        listTradeReports({ accountId: account, limit: 50 }),
      ]);

      if (!posResult.ok) {
        handleFailure(posResult, setPositionsStatus, () => setPositions([]));
      } else {
        setPositions(posResult.data);
        setPositionsStatus({
          kind: "ok",
          message:
            posResult.data.length === 0
              ? "Không có position mở (empty list từ server)."
              : null,
        });
      }

      if (!pnlResult.ok) {
        handleFailure(pnlResult, setPnlStatus, () => setPnl(null));
      } else {
        setPnl(pnlResult.data);
        setPnlStatus({ kind: "ok", message: null });
      }

      if (!tradesResult.ok) {
        handleFailure(tradesResult, setActivityStatus, () => setTrades([]));
      } else {
        setTrades(tradesResult.data);
        setActivityStatus({
          kind: "ok",
          message:
            tradesResult.data.length === 0
              ? "Không có trade activity (empty list từ server)."
              : null,
        });
      }

      setBusy(false);
    },
    [handleFailure],
  );

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const account = accountId.trim();
    if (!account) {
      setPositionsStatus({
        kind: "err",
        message: "Cần account_id (OpenAPI bắt buộc cho cả ba GET).",
      });
      return;
    }
    await loadAll(account);
  }

  if (!ready) {
    return (
      <p className="text-sm text-neutral-600">Đang kiểm tra phiên…</p>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Positions, PnL summary, và activity — chỉ hiển thị field từ server. Không
        tính PnL phía client.
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
          href="/login"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          Login
        </Link>
      </p>

      <form onSubmit={onSubmit} className="mt-6 flex flex-wrap items-end gap-3">
        <div className="min-w-[16rem] flex-1">
          <label htmlFor="dash-account-id" className="block text-sm font-medium">
            Account ID
          </label>
          <input
            id="dash-account-id"
            name="account_id"
            type="text"
            required
            value={accountId}
            onChange={(ev) => setAccountId(ev.target.value)}
            placeholder="uuid"
            className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 font-mono text-xs outline-none focus:border-neutral-500"
          />
        </div>
        <button
          type="submit"
          disabled={busy}
          className="rounded border border-neutral-800 bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
        >
          {busy ? "Đang tải…" : "Tải dữ liệu"}
        </button>
      </form>

      <section className="mt-10">
        <h2 className="text-lg font-medium">PnL summary (server)</h2>
        <StatusBanner status={pnlStatus} />
        {pnl ? (
          <dl className="mt-3 grid gap-1 text-sm text-neutral-800">
            <div>
              <dt className="inline font-medium">currency: </dt>
              <dd className="inline">{pnl.currency}</dd>
            </div>
            <div>
              <dt className="inline font-medium">realized_pnl: </dt>
              <dd className="inline font-mono">{pnl.realized_pnl}</dd>
            </div>
            <div>
              <dt className="inline font-medium">unrealized_pnl: </dt>
              <dd className="inline font-mono">{pnl.unrealized_pnl}</dd>
            </div>
            <div>
              <dt className="inline font-medium">total_pnl: </dt>
              <dd className="inline font-mono">{pnl.total_pnl}</dd>
            </div>
            {pnl.gross_profit !== undefined ? (
              <div>
                <dt className="inline font-medium">gross_profit: </dt>
                <dd className="inline font-mono">{pnl.gross_profit}</dd>
              </div>
            ) : null}
            {pnl.gross_loss !== undefined ? (
              <div>
                <dt className="inline font-medium">gross_loss: </dt>
                <dd className="inline font-mono">{pnl.gross_loss}</dd>
              </div>
            ) : null}
            {pnl.trade_count !== undefined ? (
              <div>
                <dt className="inline font-medium">trade_count: </dt>
                <dd className="inline font-mono">{pnl.trade_count}</dd>
              </div>
            ) : null}
            <div>
              <dt className="inline font-medium">calculated_at: </dt>
              <dd className="inline font-mono text-xs">{pnl.calculated_at}</dd>
            </div>
          </dl>
        ) : (
          <p className="mt-2 text-sm text-neutral-600">
            Chưa có PnL summary từ API (hoặc lỗi / 501).
          </p>
        )}
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-medium">Positions</h2>
        <StatusBanner status={positionsStatus} />
        {positions.length === 0 ? (
          <p className="mt-2 text-sm text-neutral-600">
            Không có position — API fail / 501 / empty. UI không bịa số liệu.
          </p>
        ) : (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[40rem] border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-neutral-300 text-neutral-600">
                  <th className="py-2 pr-3 font-medium">symbol</th>
                  <th className="py-2 pr-3 font-medium">side</th>
                  <th className="py-2 pr-3 font-medium">quantity</th>
                  <th className="py-2 pr-3 font-medium">entry_price</th>
                  <th className="py-2 pr-3 font-medium">mark_price</th>
                  <th className="py-2 pr-3 font-medium">unrealized_pnl</th>
                  <th className="py-2 font-medium">opened_at</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => (
                  <tr
                    key={p.id}
                    className="border-b border-neutral-100 font-mono"
                  >
                    <td className="py-1.5 pr-3">{p.symbol}</td>
                    <td className="py-1.5 pr-3">{p.side}</td>
                    <td className="py-1.5 pr-3">{p.quantity}</td>
                    <td className="py-1.5 pr-3">{p.entry_price}</td>
                    <td className="py-1.5 pr-3">
                      {p.mark_price !== undefined ? p.mark_price : "—"}
                    </td>
                    <td className="py-1.5 pr-3">
                      {p.unrealized_pnl !== undefined ? p.unrealized_pnl : "—"}
                    </td>
                    <td className="py-1.5">{p.opened_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-medium">Activity (trades)</h2>
        <StatusBanner status={activityStatus} />
        {trades.length === 0 ? (
          <p className="mt-2 text-sm text-neutral-600">
            Không có trade — API fail / 501 / empty.
          </p>
        ) : (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[40rem] border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-neutral-300 text-neutral-600">
                  <th className="py-2 pr-3 font-medium">executed_at</th>
                  <th className="py-2 pr-3 font-medium">symbol</th>
                  <th className="py-2 pr-3 font-medium">side</th>
                  <th className="py-2 pr-3 font-medium">quantity</th>
                  <th className="py-2 pr-3 font-medium">price</th>
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

function StatusBanner({ status }: { status: SectionStatus }) {
  if (!status.message) return null;
  const className =
    status.kind === "ok"
      ? "mt-3 rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900"
      : status.kind === "stub"
        ? "mt-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950"
        : "mt-3 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900";
  return (
    <div role="alert" className={className}>
      {status.message}
    </div>
  );
}
