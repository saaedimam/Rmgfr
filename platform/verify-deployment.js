// Verifies critical endpoints/services after deploy
// Env: BASE_URL (defaults to http://localhost:3000)
//      ENDPOINTS_JSON (optional JSON array of paths, defaults: ["/health"])
// Exit code: non-zero on any failure

const BASE_URL = process.env.BASE_URL || "http://localhost:3000";
let endpoints = ["/health"];
try {
  if (process.env.ENDPOINTS_JSON) endpoints = JSON.parse(process.env.ENDPOINTS_JSON);
} catch (e) {
  console.error("Invalid ENDPOINTS_JSON:", e.message);
  process.exit(2);
}

const fetchFn = globalThis.fetch || require("node-fetch").default;

const results = [];
for (const path of endpoints) {
  const url = `${BASE_URL.replace(/\/+$/, "")}${path}`;
  try {
    const res = await fetchFn(url, { method: "GET" });
    const ok = res.ok;
    results.push({ path, status: res.status, ok });
    if (!ok) console.error(`❌ ${path} -> ${res.status}`);
  } catch (err) {
    results.push({ path, status: 0, ok: false });
    console.error(`❌ ${path} -> error: ${err.message}`);
  }
}

const failed = results.filter(r => !r.ok);
for (const r of results) {
  console.log(`${r.ok ? "✅" : "❌"} ${r.path} (${r.status})`);
}
if (failed.length) {
  console.error(`\nFailures: ${failed.length}/${results.length}`);
  process.exit(1);
}
console.log(`\nAll good: ${results.length}/${results.length}`);
