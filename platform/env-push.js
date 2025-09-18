// Push selected env vars to Railway using global CLI or npx fallback.
import { spawnSync } from "node:child_process";

const RW = (spawnSync("railway", ["--version"]).status === 0)
  ? "railway"
  : "npx";
const argsBase = RW === "railway" ? [] : ["@railway/cli"];

const KEYS = [
  "NODE_ENV",
  "DATABASE_URL",
  "REDIS_URL",
  "SECRET_KEY",
  "SENTRY_DSN",
  "NEXT_PUBLIC_API_URL",
  "NEXT_PUBLIC_APP_URL",
  "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
  "CLERK_SECRET_KEY",
];

function run(cmd, args) {
  const out = spawnSync(cmd, args, { stdio: "inherit", env: process.env, shell: false });
  if (out.status !== 0) process.exit(out.status ?? 1);
}

if (!process.env.RAILWAY_TOKEN) {
  console.error("❌ RAILWAY_TOKEN missing. Set it in your shell/CI.");
  process.exit(1);
}

// Login (browserless) - safe to call multiple times
run(RW, [...argsBase, "login", "--browserless", "--token", process.env.RAILWAY_TOKEN]);

// Push variables (skip empty/undefined)
for (const k of KEYS) {
  const v = process.env[k];
  if (v && v.trim() !== "") {
    run(RW, [...argsBase, "variables", "set", `${k}=${v}`]);
  }
}

console.log("✅ Pushed env vars to Railway.");
