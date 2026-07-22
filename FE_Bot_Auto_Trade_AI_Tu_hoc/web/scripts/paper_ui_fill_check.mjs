/**
 * Auto-fill + verify paper UI against local Next + Gateway.
 * Usage: node scripts/paper_ui_fill_check.mjs <accountId>
 */
import { chromium } from "playwright";

const ACCOUNT_ID = process.argv[2];
const BASE = process.env.FE_URL || "http://localhost:3000";
const EMAIL = "operator@example.com";
const PASSWORD = "paper-dev-password";

if (!ACCOUNT_ID) {
  console.error("Usage: node scripts/paper_ui_fill_check.mjs <accountId>");
  process.exit(2);
}

const results = [];
function ok(name, cond, detail = "") {
  results.push({ name, cond, detail });
  console.log(cond ? "PASS" : "FAIL", name, detail);
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

try {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.fill("#email", EMAIL);
  await page.fill("#password", PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(800);
  const loginText = await page.textContent("body");
  ok(
    "ui_login",
    (loginText || "").includes("Đăng nhập thành công") ||
      (loginText || "").includes("đã có phiên"),
    (loginText || "").slice(0, 80),
  );

  await page.goto(`${BASE}/dashboard`, { waitUntil: "networkidle" });
  await page.fill('input[name="account_id"]', ACCOUNT_ID);
  await page.click('button:has-text("Refresh")');
  await page.waitForTimeout(1000);
  const dash = await page.textContent("body");
  ok(
    "ui_dashboard",
    !(dash || "").includes("HTTP 422") &&
      ((dash || "").includes("USDT") ||
        (dash || "").includes("position") ||
        (dash || "").includes("BTC")),
    (dash || "").includes("HTTP 422") ? "still 422" : "loaded",
  );

  await page.goto(`${BASE}/strategies`, { waitUntil: "networkidle" });
  const listInput = page.locator("#list-account-id");
  if (await listInput.count()) {
    await listInput.fill(ACCOUNT_ID);
    await page.click('button:has-text("Tải lại")');
    await page.waitForTimeout(800);
  }
  const strat = await page.textContent("body");
  ok(
    "ui_strategies_list",
    (strat || "").includes(ACCOUNT_ID) || (strat || "").includes("auto-s1"),
    (strat || "").includes("HTTP 422") ? "422" : "ok",
  );

  await page.goto(`${BASE}/alerts`, { waitUntil: "networkidle" });
  const alertAccount = page.locator('input[placeholder*="UUID"]');
  if (await alertAccount.count()) {
    await alertAccount.fill(ACCOUNT_ID);
  } else {
    await page.fill("input", ACCOUNT_ID).catch(() => {});
  }
  await page.click('button:has-text("Refresh")');
  await page.waitForTimeout(800);
  const alerts = await page.textContent("body");
  ok(
    "ui_alerts",
    !(alerts || "").includes("HTTP 422"),
    (alerts || "").includes("KILL_SWITCH")
      ? "has KILL_SWITCH"
      : (alerts || "").includes("HTTP 422")
        ? "422"
        : "no 422",
  );
} catch (e) {
  ok("ui_exception", false, String(e));
} finally {
  await browser.close();
}

const failed = results.filter((r) => !r.cond);
console.log("\n=== UI SUMMARY ===");
console.log(
  `passed=${results.length - failed.length} failed=${failed.length} total=${results.length}`,
);
if (failed.length) {
  process.exit(1);
}
console.log("RESULT: PAPER_UI_FILL_CHECK PASS");
