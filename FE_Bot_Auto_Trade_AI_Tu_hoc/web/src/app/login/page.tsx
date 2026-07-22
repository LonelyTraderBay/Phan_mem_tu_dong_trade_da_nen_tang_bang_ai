"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import {
  formatApiFailureForUi,
  login,
  logout,
} from "@/lib/auth/session";
import { hasAccessToken } from "@/lib/auth/tokenStore";

/**
 * Operator login — postAuthLogin / postAuthLogout.
 * Never renders access_token or refresh_token in the DOM.
 */
export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageKind, setMessageKind] = useState<"ok" | "err" | null>(null);
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    setSignedIn(hasAccessToken());
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
    setMessageKind(null);

    const result = await login({ email: email.trim(), password });
    setBusy(false);

    if (!result.ok) {
      setMessageKind("err");
      setMessage(formatApiFailureForUi(result));
      setSignedIn(hasAccessToken());
      return;
    }

    setPassword("");
    setSignedIn(true);
    setMessageKind("ok");
    setMessage("Đăng nhập thành công. Phiên đã lưu an toàn (token không hiện trên UI).");
  }

  async function onLogout() {
    setBusy(true);
    setMessage(null);
    setMessageKind(null);

    const result = await logout();
    setBusy(false);
    setSignedIn(false);

    if (!result.ok) {
      setMessageKind("err");
      setMessage(
        `Đã xóa token cục bộ. Server: ${formatApiFailureForUi(result)}`,
      );
      return;
    }

    if (!result.data.success) {
      setMessageKind("err");
      setMessage("Logout không xác nhận success từ server; token cục bộ đã xóa.");
      return;
    }

    setMessageKind("ok");
    setMessage("Đã đăng xuất.");
  }

  return (
    <div className="mx-auto max-w-md">
      <h1 className="text-2xl font-semibold tracking-tight">Đăng nhập</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Operator auth (paper stub) — email và mật khẩu.
      </p>

      <p className="mt-3 text-sm">
        <Link href="/" className="text-neutral-700 underline hover:text-neutral-900">
          ← Screens
        </Link>
        {" · "}
        <span className="text-neutral-500">
          Trạng thái: {signedIn ? "đã có phiên" : "chưa đăng nhập"}
        </span>
      </p>

      {message ? (
        <div
          role="alert"
          className={
            messageKind === "ok"
              ? "mt-4 rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900"
              : "mt-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900"
          }
        >
          {message}
        </div>
      ) : null}

      {!signedIn ? (
        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(ev) => setEmail(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium">
              Mật khẩu
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              minLength={8}
              value={password}
              onChange={(ev) => setPassword(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded border border-neutral-800 bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
          >
            {busy ? "Đang gửi…" : "Đăng nhập"}
          </button>
        </form>
      ) : (
        <div className="mt-6">
          <button
            type="button"
            disabled={busy}
            onClick={onLogout}
            className="w-full rounded border border-neutral-300 bg-white px-4 py-2 text-sm font-medium hover:border-neutral-500 disabled:opacity-50"
          >
            {busy ? "Đang đăng xuất…" : "Đăng xuất"}
          </button>
        </div>
      )}
    </div>
  );
}
