import Link from "next/link";

const screens = [
  { href: "/login", label: "Login" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/live", label: "Market" },
  { href: "/strategies", label: "Strategies" },
  { href: "/accounts", label: "Accounts" },
  { href: "/alerts", label: "Alerts" },
  { href: "/reports", label: "Reports" },
  { href: "/models", label: "Models (deferred)" },
  { href: "/backtests", label: "Backtests" },
  { href: "/approvals", label: "Approvals" },
] as const;

export default function HomePage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Operator hub</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Phase 1 paper stub UI — Gateway via NEXT_PUBLIC_API_URL. L1 kill-switch stays
        visible in the header.
      </p>
      <ul className="mt-6 grid gap-2 sm:grid-cols-2">
        {screens.map((screen) => (
          <li key={screen.href}>
            <Link
              href={screen.href}
              className="block rounded border border-neutral-200 bg-white px-4 py-3 text-sm font-medium hover:border-neutral-400"
            >
              {screen.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
