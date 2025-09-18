import pg from "pg";
import { readFileSync } from "fs";
import { join } from "path";

const url = process.env.DATABASE_URL;
if (!url) {
  console.log("No DATABASE_URL; skipping seed.");
  process.exit(0);
}

const { Client } = pg;
const client = new Client({ connectionString: url });

try {
  await client.connect();
  console.log("✅ DB reachable");

  // Apply schema if requested
  if (process.env.DB_APPLY_SCHEMA) {
    console.log("Applying database schema...");
    const schemaPath = join(process.cwd(), "platform", "railway-db-setup.sql");
    const schema = readFileSync(schemaPath, "utf8");
    await client.query(schema);
    console.log("✅ Schema applied successfully");
  }

  // Show table counts
  const tenantCount = await client.query("SELECT COUNT(*) FROM tenants");
  const caseCount = await client.query("SELECT COUNT(*) FROM cases");
  const eventCount = await client.query("SELECT COUNT(*) FROM events");

  console.log(`📊 Database Stats:`);
  console.log(`   Tenants: ${tenantCount.rows[0].count}`);
  console.log(`   Cases: ${caseCount.rows[0].count}`);
  console.log(`   Events: ${eventCount.rows[0].count}`);

} catch (error) {
  console.error("❌ Database error:", error.message);
  process.exit(1);
} finally {
  await client.end();
}
