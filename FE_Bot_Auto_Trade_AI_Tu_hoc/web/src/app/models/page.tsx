import Link from "next/link";

/**
 * Models — Deferred / Out of MVP for paper E2E.
 * No promote / retrain / Model Center live actions.
 */
export default function ModelsPage() {
  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold tracking-tight">Models</h1>
      <div
        role="status"
        className="mt-4 rounded border border-amber-400 bg-amber-50 px-4 py-3 text-sm text-amber-950"
      >
        <p className="font-semibold">Out of MVP / Deferred</p>
        <p className="mt-1">
          AI Model Center promote, auto-retrain, và deep-learning-primary
          signals không thuộc phạm vi In-MVP paper trading. Trang này không
          cung cấp nút promote hay thao tác model live.
        </p>
      </div>
      <p className="mt-4 text-sm text-neutral-600">
        Dùng Strategies (form đơn giản) và Dashboard để chạy paper E2E.
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
          href="/strategies"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          Strategies
        </Link>
        {" · "}
        <Link
          href="/dashboard"
          className="text-neutral-700 underline hover:text-neutral-900"
        >
          Dashboard
        </Link>
      </p>
    </div>
  );
}
