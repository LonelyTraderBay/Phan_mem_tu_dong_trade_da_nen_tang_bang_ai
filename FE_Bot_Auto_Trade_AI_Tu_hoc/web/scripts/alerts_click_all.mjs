/**
 * Login → Alerts → Account ID prefill/fill → Severity All → Ack All → Refresh.
 * Optionally seed L1 kill-switch via Gateway so inbox is not empty.
 */
import { chromium } from "playwright";

const BASE = process.env.FE_URL || "http://localhost:3000";
const API = process.env.API_URL || "http://127.0.0.1:8000";
const EMAIL = "operator@example.com";
const PASSWORD = "paper-dev-password";
const ACCOUNT_ID =
  process.argv[2] || "2433d95e-b85a-4a60-86d3-e1879a21dd0b";

async function seedKillSwitch() {
  const login = await fetch(`${API}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
  });
  if (!login.ok) throw new Error(`login ${login.status}`);
  const { access_token } = await login.json();
  const ks = await fetch(`${API}/v1/kill-switch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify({ engaged: true, reason: "auto-click alerts seed" }),
  });
  if (!ks.ok) throw new Error(`kill-switch ${ks.status}`);
  console.log("PASS seed_kill_switch_L1");
}

await seedKillSwitch();

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

try {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.fill("#email", EMAIL);
  await page.fill("#password", PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(600);

  await page.goto(`${BASE}/alerts`, { waitUntil: "networkidle" });
  const account = page.locator('input[placeholder*="UUID"], input[placeholder*="Account"]').first();
  await account.fill(ACCOUNT_ID);

  // Severity + Ack selects: first is Account already filled; then Severity, then Ack
  const selects = page.locator("select");
  const n = await selects.count();
  // Find by label proximity: Severity options include "All" and "info"
  for (let i = 0; i < n; i++) {
    const sel = selects.nth(i);
    const html = await sel.innerHTML();
    if (html.includes("info") && html.includes("warning")) {
      await sel.selectOption({ label: "All" });
      console.log("PASS click_severity_All");
    }
    if (html.includes("Open") && html.includes("Acknowledged")) {
      await sel.selectOption({ label: "All" });
      console.log("PASS click_ack_All");
    }
  }

  await page.click('button:has-text("Refresh")');
  await page.waitForTimeout(900);
  const body = (await page.textContent("body")) || "";
  const hasKs = body.includes("KILL_SWITCH");
  const emptyOnly =
    body.includes("Inbox trống") && !body.includes("KILL_SWITCH");
  console.log(hasKs ? "PASS alerts_show_KILL_SWITCH" : "FAIL alerts_show_KILL_SWITCH");
  if (emptyOnly) console.log("NOTE: inbox still empty (gateway memory may differ)");
  console.log(hasKs ? "RESULT: ALERTS_AUTO_CLICK PASS" : "RESULT: ALERTS_AUTO_CLICK FAIL");
  process.exit(hasKs ? 0 : 1);
} finally {
  await browser.close();
}
