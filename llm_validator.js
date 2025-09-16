
// /llm/llm_validator.js
// Usage: node llm_validator.js <json-file>
// Ensures strict JSON shape and citations for case summaries.
import { readFileSync } from 'fs';
import { z } from 'zod';

export const CaseSummary = z.object({
  summary: z.string().max(900),
  key_entities: z.array(z.object({ type: z.string(), id: z.string() })).max(20),
  suspected_patterns: z.array(z.string()).optional(),
  next_actions: z.array(z.string()).max(20),
  confidence: z.number().min(0).max(1),
  citations: z.array(z.object({
    artifact_type: z.enum(['event','rule','doc']),
    artifact_id: z.string()
  })).min(1)
});

function main() {
  const path = process.argv[2];
  if (!path) {
    console.error('Usage: node llm_validator.js <json-file>');
    process.exit(2);
  }
  const raw = readFileSync(path, 'utf8');
  let obj;
  try { obj = JSON.parse(raw); }
  catch(e){ console.error('Invalid JSON:', e.message); process.exit(2); }

  const res = CaseSummary.safeParse(obj);
  if (!res.success) {
    console.error('Schema validation failed:');
    for (const issue of res.error.issues) {
      console.error('-', issue.path.join('.'), issue.message);
    }
    process.exit(1);
  }
  if (!res.data.citations || res.data.citations.length === 0) {
    console.error('Missing citations.');
    process.exit(1);
  }
  console.log('OK');
}

if (require.main === module) {
  main();
}
