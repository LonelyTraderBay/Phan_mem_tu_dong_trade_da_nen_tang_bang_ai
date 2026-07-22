"use client";

import type { ReactNode } from "react";
import { formatApiError } from "@/lib/api/errors";

type Props = {
  error: unknown;
  className?: string;
};

/** Shared Error / 401 / 501 banner — shows message + code; never invents success. */
export function ApiErrorBanner({ error, className = "" }: Props) {
  if (!error) return null;
  return (
    <div
      role="alert"
      className={`rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800 ${className}`}
    >
      {formatApiError(error)}
    </div>
  );
}

export function StaleBanner({ show, reason }: { show: boolean; reason?: string }) {
  if (!show) return null;
  return (
    <div
      role="status"
      className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900"
    >
      {reason ?? "Market data may be stale. Do not treat candles as live."}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <p className="text-sm text-neutral-500">{children}</p>;
}
