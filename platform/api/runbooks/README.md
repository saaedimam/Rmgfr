# Runbooks

## RB-001: Error Rate Spike
- Check SLO dashboard. If error_rate > 1% and p99.9 > 400ms:
  1) Enter Stabilize Mode (`/dashboard/audit/stabilize`)
  2) Verify auto-rollback result in audit timeline
  3) If persists: disable `beta_ui` & `experimental_rules` flags
  4) Page on-call; attach Sentry issue link and latest deploy id

## RB-002: Database Saturation
- Actions:
  1) Enable Stabilize
  2) Raise read replicas / reduce pool by 20%
  3) Turn off heavy jobs: `reports`, `analytics`
  4) Add index if hotspot (temporary); plan long-term fix

## RB-003: Push Failure Storm
- Actions:
  1) Deprioritize `emails,reports` queues
  2) Reduce push batch size to 50
  3) Switch to fallback provider
