# Launch Day Run-of-Show

## T-24h
- [ ] Freeze main except hotfix path
- [ ] Backups green; rollback point tagged
- [ ] Canary live at 5% traffic

## T-0h
- [ ] Promote prod; enter **canary guard** (Step 11 budgets)
- [ ] Staff on-call bridge + status page

## T+2h
- [ ] Expand to 25%; check SLO + Sentry error budget
- [ ] If burn > thresholds → auto rollback (Step 10) or Stabilize

## T+24h
- [ ] 50% → 100% if clean

## T+48h
- [ ] Post-launch review; remove freeze

## Final Checklist (tick before flipping 100%)
- [ ] WAF/rate-limits active (edge + API)
- [ ] Backups verified + last PITR drill date < 90 days
- [ ] DR flipbook reviewed by on-call
- [ ] SLO dashboards & budget policies green
- [ ] Auto-rollback tested on staging
- [ ] Secrets rotated, mTLS validated where possible
- [ ] PII scrubbing & retention jobs scheduled
- [ ] Mobile phased rollout plan set
- [ ] DNS + TLS + HSTS verified
- [ ] Status page & comms templates ready
