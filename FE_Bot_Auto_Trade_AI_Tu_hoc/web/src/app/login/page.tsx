"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { setTokenPair } from "@/lib/api/auth-storage";
import { postAuthLogin } from "@/lib/api/client";
import { ApiErrorBanner } from "@/lib/api/ui";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("operator@paper.local");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await postAuthLogin({ email: email.trim(), password });
      // sessionStorage: access for Authorization; refresh stored but never shown in UI
      setTokenPair(res.data.access_token, res.data.refresh_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <h1 className="text-2xl font-semibold tracking-tight">Login</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Paper hint: <code className="text-xs">operator@paper.local</code> — password
        from BE docs (paper stub password from BE docs).
      </p>

      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <label className="block text-sm">
          <span className="font-medium">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
            autoComplete="username"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium">Password</span>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2"
            autoComplete="current-password"
            placeholder="paper stub password from BE docs"
          />
        </label>
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded bg-neutral-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>

      {error ? <ApiErrorBanner error={error} className="mt-4" /> : null}

      <p className="mt-6 text-sm text-neutral-500">
        <Link href="/" className="underline">
          Back to home
        </Link>
      </p>
    </div>
  );
}
