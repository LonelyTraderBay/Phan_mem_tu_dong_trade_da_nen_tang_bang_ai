"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  formatApiFailureForUi,
  getAlerts,
} from "@/lib/alerts/api";
import {
  ALERT_SEVERITIES,
  type Alert,
  type AlertSeverity,
} from "@/lib/alerts/types";
import {
  getLastAccountId,
  setLastAccountId,
} from "@/lib/accounts/lastAccountId";
import { hasAccessToken } from "@/lib/auth/tokenStore";

type MessageKind = "err" | "stub" | "ok";

/**
 * Alerts inbox — getAlerts. Login redirect when unauthenticated / 401.
 */
export default function AlertsPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageKind, setMessageKind] = useState<MessageKind | null>(null);

  const [accountId, setAccountId] = useState("");
  const [severity, setSeverity] = useState<AlertSeverity | "">("");
  const [acknowledged, setAcknowledged] = useState<"all" | "open" | "acked">(
    "all",
  );

  const loadAlerts = useCallback(async () => {
    setBusy(true);
    setMessage(null);
    setMessageKind(null);

    const aid = accountId.trim();
    if (!aid) {
      setBusy(false);
      setAlerts([]);
      setMessageKind("err");
      setMessage("Cần Account ID (UUID từ trang Accounts) — OpenAPI bắt buộc.");
      return;
    }

    const result = await getAlerts({
      account_id: aid,
      ...(severity ? { severity } : {}),
      ...(acknowledged === "open"
        ? { acknowledged: false }
        : acknowledged === "acked"
          ? { acknowledged: true }
          : {}),
      limit: 50,
    });
    setBusy(false);

    if (!result.ok) {
      setAlerts([]);
      setMessageKind(
        result.kind === "stub_not_implemented" ? "stub" : "err",
      );
      setMessage(formatApiFailureForUi(result));
      if (result.kind === "unauthorized") {
        router.replace("/login");
      }
      return;
    }

    setAlerts(result.data);
    setMessageKind("ok");
    setMessage(
      result.data.length === 0
        ? "Không có alert từ API (empty list)."
        : `${result.data.length} alert(s) — codes/messages từ server.`,
    );
  }, [accountId, acknowledged, router, severity]);

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }
    const last = getLastAccountId();
    if (last) setAccountId(last);
    setReady(true);
  }, [router]);

  useEffect(() => {
    if (!ready || !accountId.trim()) return;
    void loadAlerts();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional prefill load
  }, [ready]);

  if (!ready) {
    return (
      <p className="text-sm text-neutral-600">Đang kiểm tra phiên…</p>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Alerts</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Inbox vận hành — hiển thị <code className="text-xs">code</code> +{" "}
        <code className="text-xs">message</code> từ getAlerts (server). Không
        secrets. Chú ý mã{" "}
        <code className="text-xs">RECON_MISMATCH</code>,{" "}
        <code className="text-xs">KILL_SWITCH_ACTIVE</code>,{" "}
        <code className="text-xs">KILL_SWITCH_L2_PLUS</code>.
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

      <div className="mt-4 flex flex-wrap items-end gap-3">
        <label className="block text-sm">
          <span className="text-neutral-600">Account ID</span>
          <input
            className="mt-1 block w-80 rounded border border-neutral-300 bg-white px-2 py-1.5 font-mono text-xs"
            value={accountId}
            onChange={(e) => {
              setAccountId(e.target.value);
              if (e.target.value.trim()) setLastAccountId(e.target.value);
            }}
            placeholder="UUID từ Accounts (prefill session)"
            disabled={busy}
          />
        </label>
        <label className="block text-sm">
          <span className="text-neutral-600">Severity</span>
          <select
            className="mt-1 block rounded border border-neutral-300 bg-white px-2 py-1.5"
            value={severity}
            onChange={(e) =>
              setSeverity(e.target.value as AlertSeverity | "")
            }
            disabled={busy}
          >
            <option value="">All</option>
            {ALERT_SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm">
          <span className="text-neutral-600">Ack</span>
          <select
            className="mt-1 block rounded border border-neutral-300 bg-white px-2 py-1.5"
            value={acknowledged}
            onChange={(e) =>
              setAcknowledged(e.target.value as "all" | "open" | "acked")
            }
            disabled={busy}
          >
            <option value="all">All</option>
            <option value="open">Open</option>
            <option value="acked">Acknowledged</option>
          </select>
        </label>

        <button
          type="button"
          onClick={() => void loadAlerts()}
          disabled={busy}
          className="rounded border border-neutral-800 bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
        >
          {busy ? "Loading…" : "Refresh"}
        </button>
      </div>

      {message ? (
        <div
          role="status"
          className={
            messageKind === "stub"
              ? "mt-4 rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950"
              : messageKind === "err"
                ? "mt-4 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-950"
                : "mt-4 rounded border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-700"
          }
        >
          {message}
        </div>
      ) : null}

      <ul className="mt-4 divide-y divide-neutral-200 border border-neutral-200 bg-white">
        {alerts.length === 0 && !busy ? (
          <li className="px-3 py-4 text-sm text-neutral-500">
            Inbox trống — không có alert từ API (hoặc bộ lọc không khớp).
          </li>
        ) : null}
        {alerts.map((alert) => (
          <li key={alert.id} className="px-3 py-3 text-sm">
            <div className="flex flex-wrap items-baseline gap-2">
              <span
                className={
                  alert.severity === "critical"
                    ? "font-semibold uppercase text-red-700"
                    : alert.severity === "warning"
                      ? "font-semibold uppercase text-amber-700"
                      : "font-semibold uppercase text-neutral-600"
                }
              >
                {alert.severity}
              </span>
              <code className="rounded bg-neutral-100 px-1.5 py-0.5 text-xs font-medium text-neutral-800">
                {alert.code}
              </code>
              <span className="text-xs text-neutral-400">
                {alert.created_at}
              </span>
              {alert.acknowledged ? (
                <span className="text-xs text-neutral-500">acked</span>
              ) : (
                <span className="text-xs font-medium text-neutral-800">
                  open
                </span>
              )}
            </div>
            <p className="mt-1 text-neutral-900">{alert.message}</p>
            {alert.account_id ? (
              <p className="mt-1 text-xs text-neutral-500">
                account: {alert.account_id}
              </p>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
