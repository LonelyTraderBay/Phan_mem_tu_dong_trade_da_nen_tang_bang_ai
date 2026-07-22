"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  formatApiFailureForUi,
  listMarketCandles,
  listMarketSymbols,
} from "@/lib/market/api";
import {
  CANDLE_INTERVALS,
  type Candle,
  type CandleInterval,
  type MarketSymbol,
} from "@/lib/market/types";
import type { ApiFailure } from "@/lib/api/client";
import { hasAccessToken } from "@/lib/auth/tokenStore";

type StaleReason = "api_error" | "stub_501" | "header";

/**
 * Paper market visibility — getMarketSymbols + getMarketCandles.
 * STALE when API fails, 501, or X-Market-Stale: true. Never invent OHLCV.
 */
export default function LivePage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  const [symbols, setSymbols] = useState<MarketSymbol[]>([]);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [candleInterval, setCandleInterval] = useState<CandleInterval>("1h");

  const [busy, setBusy] = useState(false);
  const [symbolsStale, setSymbolsStale] = useState(false);
  const [candlesStale, setCandlesStale] = useState(false);
  const [staleReason, setStaleReason] = useState<StaleReason | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const stale = symbolsStale || candlesStale;

  const applyFailure = useCallback(
    (result: ApiFailure, scope: "symbols" | "candles") => {
      if (scope === "symbols") {
        setSymbols([]);
        setSelectedSymbol("");
        setCandles([]);
        setSymbolsStale(true);
        setCandlesStale(true);
      } else {
        setCandles([]);
        setCandlesStale(true);
      }
      setStaleReason(
        result.kind === "stub_not_implemented" ? "stub_501" : "api_error",
      );
      setMessage(formatApiFailureForUi(result));
      if (result.kind === "unauthorized") {
        router.replace("/login");
      }
    },
    [router],
  );

  const loadSymbols = useCallback(async () => {
    setBusy(true);
    const result = await listMarketSymbols();
    setBusy(false);

    if (!result.ok) {
      applyFailure(result, "symbols");
      return;
    }

    setSymbols(result.data);
    setSymbolsStale(result.stale);
    if (result.stale) {
      setStaleReason("header");
      setMessage("Feed đánh dấu stale (X-Market-Stale).");
    }

    if (result.data.length === 0) {
      setSelectedSymbol("");
      setCandles([]);
      return;
    }

    setSelectedSymbol((prev) =>
      prev && result.data.some((s) => s.symbol === prev)
        ? prev
        : result.data[0].symbol,
    );
  }, [applyFailure]);

  const loadCandles = useCallback(
    async (symbol: string, interval: CandleInterval) => {
      if (!symbol) {
        setCandles([]);
        return;
      }

      setBusy(true);
      const result = await listMarketCandles({
        symbol,
        interval,
        limit: 50,
      });
      setBusy(false);

      if (!result.ok) {
        // Fail-closed: never fabricate OHLCV on error / 501.
        applyFailure(result, "candles");
        return;
      }

      setCandles(result.data);
      setCandlesStale(result.stale);
      if (result.stale) {
        setStaleReason("header");
        setMessage("Feed đánh dấu stale (X-Market-Stale).");
      }
    },
    [applyFailure],
  );

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  useEffect(() => {
    if (!ready) return;
    void loadSymbols();
  }, [ready, loadSymbols]);

  useEffect(() => {
    if (!ready || !selectedSymbol) return;
    void loadCandles(selectedSymbol, candleInterval);
  }, [ready, selectedSymbol, candleInterval, loadCandles]);

  useEffect(() => {
    if (!symbolsStale && !candlesStale) {
      setStaleReason(null);
      setMessage(null);
    }
  }, [symbolsStale, candlesStale]);

  if (!ready) {
    return (
      <p className="text-sm text-neutral-600">Đang kiểm tra phiên…</p>
    );
  }

  const staleLabel =
    staleReason === "stub_501"
      ? "STALE — endpoint chưa sẵn sàng (501)"
      : staleReason === "header"
        ? "STALE — X-Market-Stale"
        : staleReason === "api_error"
          ? "STALE — lỗi tải market data"
          : "STALE";

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-2xl font-semibold tracking-tight">Live / Market</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Paper market visibility — symbols + candles. Không bịa nến khi API lỗi.
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

      {stale ? (
        <div
          role="status"
          aria-live="polite"
          className="mt-4 rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-950"
        >
          {staleLabel}
          {message ? (
            <span className="mt-1 block font-normal text-amber-900">
              {message}
            </span>
          ) : null}
        </div>
      ) : null}

      <section className="mt-8">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[10rem] flex-1">
            <label htmlFor="market-symbol" className="block text-sm font-medium">
              Symbol
            </label>
            <select
              id="market-symbol"
              value={selectedSymbol}
              disabled={busy || symbols.length === 0}
              onChange={(ev) => setSelectedSymbol(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500 disabled:opacity-50"
            >
              {symbols.length === 0 ? (
                <option value="">(không có symbol)</option>
              ) : (
                symbols.map((s) => (
                  <option key={`${s.exchange}:${s.symbol}`} value={s.symbol}>
                    {s.symbol} · {s.exchange} · {s.market_type}
                    {s.active ? "" : " (inactive)"}
                  </option>
                ))
              )}
            </select>
          </div>
          <div>
            <label
              htmlFor="market-interval"
              className="block text-sm font-medium"
            >
              Interval
            </label>
            <select
              id="market-interval"
              value={candleInterval}
              disabled={busy}
              onChange={(ev) =>
                setCandleInterval(ev.target.value as CandleInterval)
              }
              className="mt-1 rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500 disabled:opacity-50"
            >
              {CANDLE_INTERVALS.map((tf) => (
                <option key={tf} value={tf}>
                  {tf}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            disabled={busy}
            onClick={() => {
              void loadSymbols();
            }}
            className="rounded border border-neutral-400 bg-white px-4 py-2 text-sm font-medium hover:bg-neutral-50 disabled:opacity-50"
          >
            {busy ? "Đang tải…" : "Tải lại"}
          </button>
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-medium">Symbols</h2>
        {symbols.length === 0 ? (
          <p className="mt-2 text-sm text-neutral-600">
            Chưa có symbol từ API (hoặc lỗi / 501 — không hiển thị dữ liệu giả).
          </p>
        ) : (
          <ul className="mt-3 max-h-40 overflow-auto text-sm">
            {symbols.map((s) => (
              <li
                key={`${s.exchange}:${s.symbol}`}
                className="border-b border-neutral-100 py-1.5 font-mono text-xs"
              >
                {s.symbol} · {s.base_asset}/{s.quote_asset} · {s.exchange} ·{" "}
                {s.market_type} · {s.active ? "active" : "inactive"}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-medium">Candles (OHLCV)</h2>
        {candles.length === 0 ? (
          <p className="mt-2 text-sm text-neutral-600">
            Không có nến — API fail / 501 / empty. UI không bịa OHLCV.
          </p>
        ) : (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[36rem] border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-neutral-300 text-neutral-600">
                  <th className="py-2 pr-3 font-medium">open_time</th>
                  <th className="py-2 pr-3 font-medium">O</th>
                  <th className="py-2 pr-3 font-medium">H</th>
                  <th className="py-2 pr-3 font-medium">L</th>
                  <th className="py-2 pr-3 font-medium">C</th>
                  <th className="py-2 font-medium">V</th>
                </tr>
              </thead>
              <tbody>
                {candles.map((c) => (
                  <tr
                    key={`${c.symbol}-${c.interval}-${c.open_time}`}
                    className="border-b border-neutral-100 font-mono"
                  >
                    <td className="py-1.5 pr-3">{c.open_time}</td>
                    <td className="py-1.5 pr-3">{c.open}</td>
                    <td className="py-1.5 pr-3">{c.high}</td>
                    <td className="py-1.5 pr-3">{c.low}</td>
                    <td className="py-1.5 pr-3">{c.close}</td>
                    <td className="py-1.5">{c.volume}</td>
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
