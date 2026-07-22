"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import {
  createAccount,
  createAccountApiKey,
  formatApiFailureForUi,
} from "@/lib/accounts/api";
import { setLastAccountId } from "@/lib/accounts/lastAccountId";
import type {
  Account,
  ApiKeyMasked,
  MarketType,
} from "@/lib/accounts/types";
import { hasAccessToken } from "@/lib/auth/tokenStore";

type MessageKind = "ok" | "err" | "stub";

/**
 * Broker credentials — postAccounts / postAccountApiKeys.
 * Never re-display full api_key / api_secret after save; only masked_api_key.
 */
export default function AccountsPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  const [name, setName] = useState("");
  const [exchange, setExchange] = useState("");
  const [marketType, setMarketType] = useState<MarketType>("spot");
  const [testnet, setTestnet] = useState(true);

  const [accountId, setAccountId] = useState("");
  const [createdAccount, setCreatedAccount] = useState<Account | null>(null);

  const [label, setLabel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [passphrase, setPassphrase] = useState("");
  const [maskedKey, setMaskedKey] = useState<ApiKeyMasked | null>(null);

  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageKind, setMessageKind] = useState<MessageKind | null>(null);

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  async function onCreateAccount(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
    setMessageKind(null);

    const result = await createAccount({
      name: name.trim(),
      exchange: exchange.trim(),
      market_type: marketType,
      testnet,
    });
    setBusy(false);

    if (!result.ok) {
      setMessageKind(result.kind === "stub_not_implemented" ? "stub" : "err");
      setMessage(formatApiFailureForUi(result));
      if (result.kind === "unauthorized") {
        router.replace("/login");
      }
      return;
    }

    setCreatedAccount(result.data);
    setAccountId(result.data.id);
    setLastAccountId(result.data.id);
    setMessageKind("ok");
    setMessage(
      `Account đã tạo (id: ${result.data.id}). Tiếp tục gắn API key bên dưới. ID đã nhớ cho Strategies/Dashboard/Alerts.`,
    );
  }

  async function onCreateApiKey(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
    setMessageKind(null);

    const targetAccountId = accountId.trim();
    if (!targetAccountId) {
      setBusy(false);
      setMessageKind("err");
      setMessage("Cần account_id (tạo account trước hoặc dán UUID).");
      return;
    }

    const body = {
      label: label.trim(),
      api_key: apiKey,
      api_secret: apiSecret,
      ...(passphrase.trim().length > 0
        ? { passphrase: passphrase.trim() }
        : {}),
    };

    const result = await createAccountApiKey(targetAccountId, body);

    // Clear secrets from React state immediately after the request returns
    // (success or failure) so full secret is never retained post-submit UX.
    setApiKey("");
    setApiSecret("");
    setPassphrase("");
    setBusy(false);

    if (!result.ok) {
      setMaskedKey(null);
      setMessageKind(result.kind === "stub_not_implemented" ? "stub" : "err");
      if (result.kind === "stub_not_implemented") {
        setMessage(
          `${formatApiFailureForUi(result)} — chưa xác nhận kết nối live.`,
        );
      } else {
        setMessage(formatApiFailureForUi(result));
      }
      if (result.kind === "unauthorized") {
        router.replace("/login");
      }
      return;
    }

    setMaskedKey(result.data);
    setMessageKind("ok");
    setMessage(
      "API key đã lưu (masked). Secret đầy đủ không còn trên form và không được hiển thị lại.",
    );
  }

  if (!ready) {
    return (
      <p className="text-sm text-neutral-600">Đang kiểm tra phiên…</p>
    );
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="text-2xl font-semibold tracking-tight">Accounts</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Đăng ký tài khoản paper và API key sàn — chỉ hiển thị key đã mask sau khi
        lưu.
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

      <div
        role="note"
        className="mt-4 rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950"
      >
        <strong className="font-medium">Bắt buộc trước khi kết nối:</strong> tắt
        quyền rút tiền (withdraw / transfer) trên API key sàn. Chỉ cấp quyền
        trade — không cấp quyền rút tiền.
      </div>

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
        <h2 className="text-lg font-medium">1. Tạo account</h2>
        <form onSubmit={onCreateAccount} className="mt-4 space-y-4">
          <div>
            <label htmlFor="account-name" className="block text-sm font-medium">
              Name
            </label>
            <input
              id="account-name"
              name="name"
              type="text"
              required
              minLength={1}
              maxLength={100}
              value={name}
              onChange={(ev) => setName(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label
              htmlFor="account-exchange"
              className="block text-sm font-medium"
            >
              Exchange
            </label>
            <input
              id="account-exchange"
              name="exchange"
              type="text"
              required
              minLength={1}
              placeholder="binance"
              value={exchange}
              onChange={(ev) => setExchange(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label
              htmlFor="account-market-type"
              className="block text-sm font-medium"
            >
              Market type
            </label>
            <select
              id="account-market-type"
              name="market_type"
              required
              value={marketType}
              onChange={(ev) =>
                setMarketType(ev.target.value as MarketType)
              }
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            >
              <option value="spot">spot</option>
              <option value="futures">futures</option>
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              name="testnet"
              checked={testnet}
              onChange={(ev) => setTestnet(ev.target.checked)}
            />
            Testnet / paper (khuyến nghị)
          </label>
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded border border-neutral-800 bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
          >
            {busy ? "Đang gửi…" : "Tạo account"}
          </button>
        </form>

        {createdAccount ? (
          <dl className="mt-4 grid gap-1 text-sm text-neutral-700">
            <div>
              <dt className="inline font-medium">id: </dt>
              <dd className="inline font-mono text-xs">{createdAccount.id}</dd>
            </div>
            <div>
              <dt className="inline font-medium">status: </dt>
              <dd className="inline">{createdAccount.status}</dd>
            </div>
            <div>
              <dt className="inline font-medium">testnet: </dt>
              <dd className="inline">{createdAccount.testnet ? "yes" : "no"}</dd>
            </div>
          </dl>
        ) : null}
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-medium">2. Gắn API key</h2>
        <form onSubmit={onCreateApiKey} className="mt-4 space-y-4">
          <div>
            <label htmlFor="account-id" className="block text-sm font-medium">
              Account ID
            </label>
            <input
              id="account-id"
              name="account_id"
              type="text"
              required
              value={accountId}
              onChange={(ev) => setAccountId(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 font-mono text-xs outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label htmlFor="key-label" className="block text-sm font-medium">
              Label
            </label>
            <input
              id="key-label"
              name="label"
              type="text"
              required
              minLength={1}
              maxLength={100}
              value={label}
              onChange={(ev) => setLabel(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label htmlFor="api-key" className="block text-sm font-medium">
              API key
            </label>
            <input
              id="api-key"
              name="api_key"
              type="password"
              autoComplete="off"
              required
              minLength={1}
              value={apiKey}
              onChange={(ev) => setApiKey(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label htmlFor="api-secret" className="block text-sm font-medium">
              API secret
            </label>
            <input
              id="api-secret"
              name="api_secret"
              type="password"
              autoComplete="off"
              required
              minLength={1}
              value={apiSecret}
              onChange={(ev) => setApiSecret(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label htmlFor="passphrase" className="block text-sm font-medium">
              Passphrase (tuỳ chọn)
            </label>
            <input
              id="passphrase"
              name="passphrase"
              type="password"
              autoComplete="off"
              minLength={1}
              value={passphrase}
              onChange={(ev) => setPassphrase(ev.target.value)}
              className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-500"
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded border border-neutral-800 bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
          >
            {busy ? "Đang gửi…" : "Lưu API key"}
          </button>
        </form>

        {maskedKey ? (
          <div className="mt-4 rounded border border-neutral-200 bg-white px-3 py-3 text-sm">
            <p className="font-medium">Đã lưu (masked only)</p>
            <p className="mt-1 font-mono text-xs">
              {maskedKey.masked_api_key}
            </p>
            <p className="mt-1 text-neutral-600">
              label: {maskedKey.label} · id: {maskedKey.id}
            </p>
          </div>
        ) : null}
      </section>
    </div>
  );
}
