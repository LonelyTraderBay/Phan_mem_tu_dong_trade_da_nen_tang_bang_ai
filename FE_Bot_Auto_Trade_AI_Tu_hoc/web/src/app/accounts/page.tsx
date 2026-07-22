"use client";

import { useState, type FormEvent } from "react";
import { AccountIdInput } from "@/components/AccountIdInput";
import { RequireAuth } from "@/components/RequireAuth";
import { setStoredAccountId } from "@/lib/api/auth-storage";
import { postAccountApiKeys, postAccounts } from "@/lib/api/client";
import type { Account, ApiKeyMasked, MarketType } from "@/lib/api/types";
import { ApiErrorBanner, EmptyState } from "@/lib/api/ui";

function AccountsInner() {
  const [name, setName] = useState("paper-binance");
  const [exchange, setExchange] = useState("binance");
  const [marketType, setMarketType] = useState<MarketType>("futures");
  const [testnet, setTestnet] = useState(true);

  const [accountId, setAccountId] = useState("");
  const [label, setLabel] = useState("primary");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [passphrase, setPassphrase] = useState("");

  const [account, setAccount] = useState<Account | null>(null);
  const [masked, setMasked] = useState<ApiKeyMasked | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function onCreateAccount(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setMasked(null);
    try {
      const res = await postAccounts({
        name: name.trim(),
        exchange: exchange.trim(),
        market_type: marketType,
        testnet,
      });
      setAccount(res.data);
      setAccountId(res.data.id);
      setStoredAccountId(res.data.id);
      // Clear any prior secret fields after successful account create path
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function onRegisterKeys(e: FormEvent) {
    e.preventDefault();
    if (!accountId.trim()) {
      setError(new Error("Account ID required"));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await postAccountApiKeys(accountId.trim(), {
        label: label.trim(),
        api_key: apiKey,
        api_secret: apiSecret,
        ...(passphrase ? { passphrase } : {}),
      });
      setMasked(res.data);
      // Never re-display full secret — clear inputs after save
      setApiKey("");
      setApiSecret("");
      setPassphrase("");
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Accounts</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Create account and register API keys. After save, only masked key is shown.
        </p>
      </div>

      {error ? <ApiErrorBanner error={error} /> : null}

      <form onSubmit={onCreateAccount} className="space-y-3 rounded border border-neutral-200 bg-white p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Create account
        </h2>
        <label className="block text-sm">
          <span className="font-medium">Name</span>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">Exchange</span>
          <input
            required
            value={exchange}
            onChange={(e) => setExchange(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">Market type</span>
          <select
            value={marketType}
            onChange={(e) => setMarketType(e.target.value as MarketType)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
          >
            <option value="spot">spot</option>
            <option value="futures">futures</option>
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={testnet}
            onChange={(e) => setTestnet(e.target.checked)}
          />
          Testnet / paper
        </label>
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-neutral-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Create
        </button>
        {account ? (
          <p className="text-sm text-neutral-700">
            Created <span className="font-mono">{account.id}</span> · {account.status} ·{" "}
            {account.exchange}/{account.market_type}
          </p>
        ) : null}
      </form>

      <form onSubmit={onRegisterKeys} className="space-y-3 rounded border border-neutral-200 bg-white p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Register API keys
        </h2>
        <AccountIdInput value={accountId} onChange={setAccountId} />
        <label className="block text-sm">
          <span className="font-medium">Label</span>
          <input
            required
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">API key</span>
          <input
            required
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
            autoComplete="off"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">API secret</span>
          <input
            required
            type="password"
            value={apiSecret}
            onChange={(e) => setApiSecret(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
            autoComplete="off"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">Passphrase (optional)</span>
          <input
            type="password"
            value={passphrase}
            onChange={(e) => setPassphrase(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
            autoComplete="off"
          />
        </label>
        <p className="text-xs text-neutral-500">
          Disable withdraw on exchange keys. Secrets are cleared from the form after save.
        </p>
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-neutral-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Register keys
        </button>
        {masked ? (
          <div className="rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm">
            <p>
              Saved <span className="font-medium">{masked.label}</span>
            </p>
            <p className="font-mono">masked: {masked.masked_api_key}</p>
            <EmptyState>Full secret is not available after save.</EmptyState>
          </div>
        ) : null}
      </form>
    </div>
  );
}

export default function AccountsPage() {
  return (
    <RequireAuth>
      <AccountsInner />
    </RequireAuth>
  );
}
