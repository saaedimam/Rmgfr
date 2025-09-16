# Day-30 Optimization Plan

## Performance
- [ ] Bundle ≤ 300KB audit
- [ ] Image optimization audit
- [ ] DB slow query index pass
- [ ] CDN cache hit ratio optimization

## Reliability
- [ ] Chaos drills (pod kill, DB failover)
- [ ] Verify auto-rollback in real traffic window
- [ ] Load testing with production-like data
- [ ] Circuit breaker tuning

## Cost
- [ ] Right-size instances based on actual usage
- [ ] Storage lifecycle for objects/logs
- [ ] Sentry sampling to 0.2
- [ ] Redis memory optimization

## Security
- [ ] Quarterly key rotation
- [ ] SCA baseline scan
- [ ] Dependency review and updates
- [ ] Penetration testing

## Product
- [ ] Flags cleanup (retire canary gates)
- [ ] Define next quarter's SLOs
- [ ] Feature flag analytics
- [ ] User feedback integration
