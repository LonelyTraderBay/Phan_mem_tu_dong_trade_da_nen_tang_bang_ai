"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  isAuthenticated,
} from "@/lib/api/auth-storage";
import { postAuthLogout } from "@/lib/api/client";
import { ApiErrorBanner } from "@/lib/api/ui";

const links = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/live", label: "Market" },
  { href: "/strategies", label: "Strategies" },
  { href: "/accounts", label: "Accounts" },
  { href: "/alerts", label: "Alerts" },
  { href: "/reports", label: "Reports" },
  { href: "/models", label: "Models" },
] as const;

export function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const [authed, setAuthed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    setAuthed(isAuthenticated());
  }, [pathname]);

  const onLogout = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const refresh = getRefreshToken();
      if (getAccessToken()) {
        try {
          await postAuthLogout(refresh ? { refresh_token: refresh } : undefined);
        } catch {
          /* still clear local session */
        }
      }
      clearTokens();
      setAuthed(false);
      router.push("/login");
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }, [router]);

  if (pathname === "/login") {
    return null;
  }

  return (
    <nav className="border-b border-neutral-200 bg-white">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-3 gap-y-2 px-4 py-2">
        <span className="mr-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Nav
        </span>
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm ${
                active
                  ? "font-semibold text-neutral-900"
                  : "text-neutral-600 hover:text-neutral-900"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
        <div className="ml-auto flex items-center gap-2">
          {authed ? (
            <button
              type="button"
              disabled={busy}
              onClick={() => void onLogout()}
              className="rounded border border-neutral-300 px-2 py-1 text-xs font-medium text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
            >
              {busy ? "Logging out…" : "Logout"}
            </button>
          ) : (
            <Link
              href="/login"
              className="rounded border border-neutral-300 px-2 py-1 text-xs font-medium text-neutral-700 hover:bg-neutral-50"
            >
              Login
            </Link>
          )}
        </div>
      </div>
      {error ? (
        <div className="mx-auto max-w-5xl px-4 pb-2">
          <ApiErrorBanner error={error} />
        </div>
      ) : null}
    </nav>
  );
}
