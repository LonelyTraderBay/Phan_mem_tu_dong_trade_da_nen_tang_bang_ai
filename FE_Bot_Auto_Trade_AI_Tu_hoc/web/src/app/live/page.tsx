"use client";

import { useState, type FormEvent } from "react";
import { RequireAuth } from "@/components/RequireAuth";
import { getMarketCandles, getMarketSymbols } from "@/lib/api/client";
import type { Candle, CandleInterval, MarketSymbol } from "@/lib/api/types";
import { ApiErrorBanner, EmptyState, StaleBanner } from "@/lib/api/ui";

const INTERVALS: CandleInterval[] = ["1m", "5m", "15m", "1h", "4h", "1d"];

function LiveInner() {
  const [symbols, setSymbols] = useState<MarketSymbol[]>([]);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [interval, setInterval] = useState<CandleInterval>("15m");
  const [stale, setStale] = useState(false);
  const [staleReason, setStaleReason] = useState<string | undefined>();
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function loadSymbols() {
    setBusy(true);
    setError(null);
    try {
      const res = await getMarketSymbols();
      setSymbols(res.data);
      setStale(res.stale);
      setStaleReason(res.stale ? "Symbols response marked stale (X-Data-Stale)." : undefined);
      if (res.data[0]?.symbol) {
        setSymbol(res.data[0].symbol);
      }
    } catch (err) {
      setSymbols([]);
      setStale(true);
      setStaleReason("Symbol request failed — feed treated as stale; no fabricated data.");
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function loadCandles(e?: FormEvent) {
    e?.preventDefault();
    setBusy(true);
    setError(null);
    setCandles([]);
    try {
      const res = await getMarketCandles({
        symbol: symbol.trim(),
        interval,
        limit: 50,
      });
      setCandles(res.data);
      setStale(res.stale);
      setStaleReason(
        res.stale ? "Candles response marked stale (X-Data-Stale)." : undefined,
      );
    } catch (err) {
      setCandles([]);
      setStale(true);
      setStaleReason("Candle request failed — no fabricated candles.");
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Market</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Symbols + candles from Gateway only. Stale banner on failure or X-Data-Stale.
        </p>
      </div>

      <StaleBanner show={stale} reason={staleReason} />
      {error ? <ApiErrorBanner error={error} /> : null}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy}
          onClick={() => void loadSymbols()}
          className="rounded bg-neutral-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Load symbols
        </button>
      </div>

      {symbols.length > 0 ? (
        <ul className="max-h-40 overflow-auto rounded border border-neutral-200 bg-white text-sm">
          {symbols.map((s) => (
            <li key={`${s.exchange}-${s.symbol}`}>
              <button
                type="button"
                className="w-full px-3 py-1.5 text-left hover:bg-neutral-50"
                onClick={() => setSymbol(s.symbol)}
              >
                <span className="font-mono">{s.symbol}</span>
                <span className="ml-2 text-neutral-500">
                  {s.exchange} · {s.market_type}
                  {s.active ? "" : " · inactive"}
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState>No symbols loaded.</EmptyState>
      )}

      <form onSubmit={(e) => void loadCandles(e)} className="flex flex-wrap items-end gap-3">
        <label className="block text-sm">
          <span className="font-medium">Symbol</span>
          <input
            required
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="mt-1 block rounded border border-neutral-300 px-3 py-2 font-mono"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">Interval</span>
          <select
            value={interval}
            onChange={(e) => setInterval(e.target.value as CandleInterval)}
            className="mt-1 block rounded border border-neutral-300 px-3 py-2"
          >
            {INTERVALS.map((i) => (
              <option key={i} value={i}>
                {i}
              </option>
            ))}
          </select>
        </label>
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-neutral-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Fetch candles
        </button>
      </form>

      {candles.length === 0 ? (
        <EmptyState>No candles to display.</EmptyState>
      ) : (
        <div className="overflow-x-auto rounded border border-neutral-200 bg-white">
          <table className="min-w-full text-left text-xs">
            <thead className="border-b border-neutral-200 bg-neutral-50 text-neutral-600">
              <tr>
                <th className="px-2 py-2">open_time</th>
                <th className="px-2 py-2">O</th>
                <th className="px-2 py-2">H</th>
                <th className="px-2 py-2">L</th>
                <th className="px-2 py-2">C</th>
                <th className="px-2 py-2">V</th>
              </tr>
            </thead>
            <tbody>
              {candles.map((c) => (
                <tr key={`${c.symbol}-${c.open_time}`} className="border-b border-neutral-100">
                  <td className="px-2 py-1 font-mono">{c.open_time}</td>
                  <td className="px-2 py-1">{c.open}</td>
                  <td className="px-2 py-1">{c.high}</td>
                  <td className="px-2 py-1">{c.low}</td>
                  <td className="px-2 py-1">{c.close}</td>
                  <td className="px-2 py-1">{c.volume}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function LivePage() {
  return (
    <RequireAuth>
      <LiveInner />
    </RequireAuth>
  );
}
