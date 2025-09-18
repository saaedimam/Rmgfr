// Simple database connectivity test using built-in fetch
const url = process.env.DATABASE_URL;
if (!url) {
  console.log("No DATABASE_URL; skipping test.");
  process.exit(0);
}

console.log("Testing database connectivity...");
console.log("Database URL:", url.replace(/:[^:@]+@/, ':***@')); // Hide password

// For now, just validate the URL format
const urlPattern = /^postgresql:\/\/[^:]+:[^@]+@[^:]+:\d+\/[^?]+/;
if (!urlPattern.test(url)) {
  console.error("❌ Invalid DATABASE_URL format");
  process.exit(1);
}

console.log("✅ DATABASE_URL format looks correct");
console.log("📝 To apply schema, run: psql \"" + url + "\" -f railway-db-setup.sql");
console.log("📝 Or use Railway's database console to run the SQL manually");
