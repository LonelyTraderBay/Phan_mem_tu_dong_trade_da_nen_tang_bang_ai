"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  createStrategy,
  formatApiFailureForUi,
  listStrategies,
  patchStrategy,
} from "@/lib/strategies/api";
import {
  STRATEGY_RUN_STATUSES,
  STRATEGY_STATUSES,
  STRATEGY_TIMEFRAMES,
  type Strategy,
  type StrategyStatus,
  type StrategyTimeframe,
} from "@/lib/strategies/types";
import type { ApiFailure } from "@/lib/api/client";
import { hasAccessToken } from "@/lib/auth/tokenStore";

type MessageKind = "ok" | "err" | "stub";

/**
 * Simple strategy form — getStrategies / postStrategies / patchStrategy.
 * No-code / drag-drop builder is Deferred (Out of MVP).
 */
export default function StrategiesPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  const [accountId, setAccountId] = useState("");
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("");
  const [timeframe, setTimeframe] = useState<StrategyTimeframe>("1h");
  const [createStatus, setCreateStatus] = useState<StrategyStatus | "">("");
  const [maxPositionSize, setMaxPositionSize] = useState("");
  const [stopLossPercent, setStopLossPercent] = useState("");

  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [listFilterAccountId, setListFilterAccountId] = useState("");

  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageKind, setMessageKind] = useState<MessageKind | null>(null);

  const handleFailure = useCallback(
    (result: ApiFailure, context?: { action?: "activate" | "create" | "patch" }) => {
      setMessageKind(result.kind === "stub_not_implemented" ? "stub" : "err");
      let text = formatApiFailureForUi(result);
      if (result.kind === "stub_not_implemented") {
        text = `${text} — chưa xác nhận chạy strategy live.`;
      }
      if (context?.action === "activate") {
        text = `${text} — Activate thất bại; status trên UI không đổi thành active.`;
      } else if (context?.action === "create") {
        text = `${text} — Create thất bại; không có strategy mới.`;
      } else if (context?.action === "patch") {
        text = `${text} — Patch thất bại; status trên UI giữ nguyên.`;
      }
      setMessage(text);
      if (result.kind === "unauthorized") {
        router.replace("/login");
      }
    },
    [router],
  );

  const refreshList = useCallback(
    async (filterAccountId?: string): Promise<boolean> => {
      const account = (filterAccountId ?? listFilterAccountId).trim();
      if (!account) {
        setStrategies([]);
        setMessageKind("err");
        setMessage("Cần account_id để gọi getStrategies (OpenAPI bắt buộc).");
        return false;
      }
      const result = await listStrategies({ accountId: account });
      if (!result.ok) {
        handleFailure(result);
        return false;
      }
      setStrategies(result.data);
      return true;
    },
    [handleFailure, listFilterAccountId],
  );

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  async function onCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
    setMessageKind(null);

    const body: Parameters<typeof createStrategy>[0] = {
      account_id: accountId.trim(),
      name: name.trim(),
      symbol: symbol.trim(),
      timeframe,
    };
    if (createStatus) {
      body.status = createStatus;
    }
    const maxSize = maxPositionSize.trim();
    if (maxSize.length > 0) {
      const n = Number(maxSize);
      if (!Number.isFinite(n) || n < 0) {
        setBusy(false);
        setMessageKind("err");
        setMessage("max_position_size phải là số ≥ 0.");
        return;
      }
      body.max_position_size = n;
    }
    const sl = stopLossPercent.trim();
    if (sl.length > 0) {
      const n = Number(sl);
      if (!Number.isFinite(n) || n <= 0 || n > 100) {
        setBusy(false);
        setMessageKind("err");
        setMessage("stop_loss_percent phải là số trong (0, 100].");
        return;
      }
      body.stop_loss_percent = n;
    }

    const result = await createStrategy(body);
    setBusy(false);

    if (!result.ok) {
      handleFailure(result, { action: "create" });
      return;
    }

    setMessageKind("ok");
    setMessage(`Strategy đã tạo (id: ${result.data.id}, status: ${result.data.status}).`);
    setName("");
    setSymbol("");
    setMaxPositionSize("");
    setStopLossPercent("");
    setCreateStatus("");
    if (!listFilterAccountId.trim()) {
      setListFilterAccountId(result.data.account_id);
    }
    await refreshList(result.data.account_id);
  }

  async function onPatchStatus(strategyId: string, status: StrategyStatus) {
    setBusy(true);
    setMessage(null);
    setMessageKind(null);

    const result = await patchStrategy(strategyId, { status });
    setBusy(false);

    if (!result.ok) {
      handleFailure(result, {
        action: status === "active" ? "activate" : "patch",
      });
      return;
    }

    setMessageKind("ok");
    setMessage(
      `Strategy ${result.data.id}: status → ${result.data.status} (server).`,
    );
    await refreshList(listFilterAccountId);
  }

  async function onRefreshList(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
    setMessageKind(null);
    const ok = await refreshList(listFilterAccountId);
    setBusy(false);
    if (ok) {
      setMessageKind("ok");
      setMessage("Đã tải danh sách strategies.");
    }
  }

  if (!ready) {
    return (
      <p className="text-sm text-neutral-600">Đang kiểm tra phiên…</p>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold tracking-tight">Strategies</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Form strategy đơn giản (tạo / start / pause / stop). Lỗi API
        (risk_unavailable, kill-switch, not_found) hiển thị rõ — không bịa
        success khi create/patch fail.
      </p>
      <div
        role="note"
        className="mt-3 rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950"
      >
        <strong className="font-semibold">Form-only (In-MVP).</strong> Không có
        no-code / drag-drop builder — mục đó là{" "}
        <em>Out of MVP / Deferred</em>, không có trên UI này.
      </div>

      <p className="mt-3 text-sm">
        <Link
          href="/"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          ← Screens
        </Link>
        {" · "}
        <Link
          href="/accounts"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          Accounts
        </Link>
        {" · "}
        <Link
          href="/login"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          Login
        </Link>
      </p>

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

      <section className="mt-8">
        <h2 className="text-lg font-medium">1. Tạo strategy</h2>
        <form onSubmit={onCreate} className="mt-4 space-y-4">
          <div>
            <label htmlFor="strategy-account-id" className="block text-sm font-medium">
              Account ID
            </label>
            <input
              id="strategy-account-id"
              name="account_id"
              type="text"
              required
              value={accountId}
              onChange={(ev) => setAccountId(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 font-mono text-xs outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label htmlFor="strategy-name" className="block text-sm font-medium">
              Name
            </label>
            <input
              id="strategy-name"
              name="name"
              type="text"
              required
              minLength={1}
              maxLength={120}
              value={name}
              onChange={(ev) => setName(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label htmlFor="strategy-symbol" className="block text-sm font-medium">
              Symbol
            </label>
            <input
              id="strategy-symbol"
              name="symbol"
              type="text"
              required
              minLength={1}
              placeholder="BTCUSDT"
              value={symbol}
              onChange={(ev) => setSymbol(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label
              htmlFor="strategy-timeframe"
              className="block text-sm font-medium"
            >
              Timeframe
            </label>
            <select
              id="strategy-timeframe"
              name="timeframe"
              required
              value={timeframe}
              onChange={(ev) =>
                setTimeframe(ev.target.value as StrategyTimeframe)
              }
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            >
              {STRATEGY_TIMEFRAMES.map((tf) => (
                <option key={tf} value={tf}>
                  {tf}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label
              htmlFor="strategy-create-status"
              className="block text-sm font-medium"
            >
              Status (tuỳ chọn)
            </label>
            <select
              id="strategy-create-status"
              name="status"
              value={createStatus}
              onChange={(ev) =>
                setCreateStatus(
                  (ev.target.value || "") as StrategyStatus | "",
                )
              }
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            >
              <option value="">(mặc định server)</option>
              {STRATEGY_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label
              htmlFor="strategy-max-position"
              className="block text-sm font-medium"
            >
              Max position size (tuỳ chọn)
            </label>
            <input
              id="strategy-max-position"
              name="max_position_size"
              type="number"
              min={0}
              step="any"
              value={maxPositionSize}
              onChange={(ev) => setMaxPositionSize(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label
              htmlFor="strategy-stop-loss"
              className="block text-sm font-medium"
            >
              Stop loss % (tuỳ chọn)
            </label>
            <input
              id="strategy-stop-loss"
              name="stop_loss_percent"
              type="number"
              min={0}
              max={100}
              step="any"
              value={stopLossPercent}
              onChange={(ev) => setStopLossPercent(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded border border-neutral-800 bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
          >
            {busy ? "Đang gửi…" : "Tạo strategy"}
          </button>
        </form>
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-medium">2. Danh sách &amp; start / pause / stop</h2>
        <form
          onSubmit={onRefreshList}
          className="mt-4 flex flex-wrap items-end gap-3"
        >
          <div className="min-w-[12rem] flex-1">
            <label
              htmlFor="list-account-id"
              className="block text-sm font-medium"
            >
              Account ID (bắt buộc để list)
            </label>
            <input
              id="list-account-id"
              name="list_account_id"
              type="text"
              required
              value={listFilterAccountId}
              onChange={(ev) => setListFilterAccountId(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 font-mono text-xs outline-none focus:border-neutral-500"
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            className="rounded border border-neutral-400 bg-white px-4 py-2 text-sm font-medium hover:bg-neutral-50 disabled:opacity-50"
          >
            Tải lại
          </button>
        </form>

        {strategies.length === 0 ? (
          <p className="mt-4 text-sm text-neutral-600">
            Chưa có strategy — nhập account_id rồi Tải lại, hoặc tạo mới ở trên.
          </p>
        ) : (
          <ul className="mt-4 space-y-3">
            {strategies.map((s) => (
              <li
                key={s.id}
                className="rounded border border-neutral-200 bg-white px-3 py-3 text-sm"
              >
                <div className="font-medium">{s.name}</div>
                <dl className="mt-1 grid gap-0.5 text-neutral-700">
                  <div>
                    <dt className="inline font-medium">id: </dt>
                    <dd className="inline font-mono text-xs">{s.id}</dd>
                  </div>
                  <div>
                    <dt className="inline font-medium">account: </dt>
                    <dd className="inline font-mono text-xs">{s.account_id}</dd>
                  </div>
                  <div>
                    <dt className="inline font-medium">symbol / tf: </dt>
                    <dd className="inline">
                      {s.symbol} · {s.timeframe}
                    </dd>
                  </div>
                  <div>
                    <dt className="inline font-medium">status: </dt>
                    <dd className="inline">{s.status}</dd>
                  </div>
                </dl>
                <div className="mt-3 flex flex-wrap gap-2">
                  {STRATEGY_RUN_STATUSES.map((st) => (
                    <button
                      key={st}
                      type="button"
                      disabled={busy || s.status === st}
                      onClick={() => void onPatchStatus(s.id, st)}
                      className="rounded border border-neutral-400 bg-white px-3 py-1.5 text-xs font-medium capitalize hover:bg-neutral-50 disabled:opacity-40"
                    >
                      {st === "active"
                        ? "Start (active)"
                        : st === "paused"
                          ? "Pause"
                          : "Stop"}
                    </button>
                  ))}
                  <label className="flex items-center gap-1 text-xs text-neutral-600">
                    Status
                    <select
                      aria-label={`Set status for ${s.name}`}
                      disabled={busy}
                      value={s.status}
                      onChange={(ev) => {
                        const next = ev.target.value as StrategyStatus;
                        if (next !== s.status) {
                          void onPatchStatus(s.id, next);
                        }
                      }}
                      className="rounded border border-neutral-300 bg-white px-2 py-1 text-xs outline-none focus:border-neutral-500"
                    >
                      {STRATEGY_STATUSES.map((st) => (
                        <option key={st} value={st}>
                          {st}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
