import Link from "next/link";

const screens = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/strategies", label: "Strategies" },
  { href: "/models", label: "Models" },
  { href: "/backtests", label: "Backtests" },
  { href: "/live", label: "Live" },
  { href: "/accounts", label: "Accounts" },
  { href: "/alerts", label: "Alerts" },
  { href: "/reports", label: "Reports" },
  { href: "/approvals", label: "Approvals" },
] as const;

export default function HomePage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Screens</h1>
      <p className="mt-1 text-sm text-neutral-600">
        Navigation hub — no business logic yet.
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
