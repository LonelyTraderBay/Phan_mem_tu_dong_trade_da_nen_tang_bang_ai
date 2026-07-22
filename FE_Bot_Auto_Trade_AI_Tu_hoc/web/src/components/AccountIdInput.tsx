"use client";

import { useEffect, useState } from "react";
import { getStoredAccountId, setStoredAccountId } from "@/lib/api/auth-storage";

type Props = {
  value?: string;
  onChange?: (accountId: string) => void;
  className?: string;
};

/** No GET /accounts in OpenAPI — operator pastes UUID; last id persisted in sessionStorage. */
export function AccountIdInput({ value, onChange, className = "" }: Props) {
  const [local, setLocal] = useState(value ?? "");

  useEffect(() => {
    if (value !== undefined) {
      setLocal(value);
      return;
    }
    setLocal(getStoredAccountId());
  }, [value]);

  function commit(next: string) {
    setLocal(next);
    setStoredAccountId(next.trim());
    onChange?.(next.trim());
  }

  return (
    <label className={`block text-sm ${className}`}>
      <span className="font-medium text-neutral-700">Account ID</span>
      <input
        type="text"
        value={local}
        onChange={(e) => commit(e.target.value)}
        placeholder="uuid from create account"
        className="mt-1 w-full rounded border border-neutral-300 bg-white px-3 py-2 font-mono text-sm"
        autoComplete="off"
      />
    </label>
  );
}
