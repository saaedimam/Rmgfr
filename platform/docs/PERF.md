# Performance Profiling (k6)

## Smoke (quick)
```bash
k6 run infra/load/k6_smoke.js \
  -e API_BASE=http://localhost:8000 \
  -e API_KEY=<your_api_key>
```

## Profile (sustained RPS & p99.9)

```bash
k6 run infra/load/k6_profile.js \
  -e API_BASE=http://localhost:8000 \
  -e API_KEY=<your_api_key> \
  -e RATE=100 -e DUR=5m
```

**Targets**

* `/v1/events` p99.9 < 400 ms
* `/v1/decisions` p99.9 < 400 ms
* Error rate < 1%
