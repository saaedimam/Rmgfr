// Cross-platform Railway deploy dispatcher
// Usage: npm run deploy:railway
// Env: RAILWAY_TOKEN (required), DATABASE_URL (for SQL bootstrap), SERVICE(optional), PROJECT(optional)

import { spawnSync } from "node:child_process";
import { platform } from "node:process";
import { existsSync } from "node:fs";

const isWin = platform === "win32";
const script = isWin ? "railway-deploy.ps1" : "railway-deploy.sh";

if (!existsSync(script)) {
  console.error(`Deploy script missing: ${script}`);
  process.exit(1);
}

const needsToken = !process.env.RAILWAY_TOKEN;
if (needsToken) {
  console.error("Missing RAILWAY_TOKEN. Set it in your env or CI secrets.");
  process.exit(1);
}

const cmd = isWin ? "powershell" : "bash";
const args = isWin
  ? ["-ExecutionPolicy", "Bypass", "-File", script]
  : [script];

const child = spawnSync(cmd, args, { stdio: "inherit", env: process.env });
process.exit(child.status ?? 1);
