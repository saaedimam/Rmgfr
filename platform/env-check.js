// Validates required envs at dev-time without booting the whole app.
import { spawnSync } from "node:child_process";
import { config } from "dotenv";

// Load environment variables from .env file
config();

// We rely on lib/serverEnv.ts runtime validation. Compile-run a tiny script that imports it.
const code = `
  import "./lib/serverEnv.ts";
  console.log("✅ env ok");
`;
const result = spawnSync(process.execPath, ["--input-type=module", "-e", code], {
  stdio: "inherit",
  env: process.env,
});
process.exit(result.status ?? 1);
