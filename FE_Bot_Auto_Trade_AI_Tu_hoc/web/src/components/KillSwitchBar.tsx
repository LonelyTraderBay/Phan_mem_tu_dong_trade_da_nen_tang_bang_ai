const LEVELS = ["L1", "L2", "L3", "L4"] as const;

/**
 * Stub kill-switch bar. Buttons are disabled — wire to API later.
 */
export function KillSwitchBar() {
  return (
    <header className="border-b border-neutral-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Kill switch
        </span>
        <div className="flex gap-2">
          {LEVELS.map((level) => (
            <button
              key={level}
              type="button"
              disabled
              className="rounded border border-neutral-300 bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-400"
              title="stub — not wired"
            >
              {level} <span className="font-normal">(stub)</span>
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
