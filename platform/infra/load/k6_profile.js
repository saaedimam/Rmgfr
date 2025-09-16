import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  scenarios: {
    events_rps: {
      executor: 'constant-arrival-rate',
      rate: __ENV.RATE ? Number(__ENV.RATE) : 100, // requests per second
      timeUnit: '1s',
      duration: __ENV.DUR || '2m',
      preAllocatedVUs: 50,
      maxVUs: 200,
    },
  },
  thresholds: {
    http_req_duration: ['p(99.9)<400'], // API SLO headroom
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const base = __ENV.API_BASE || 'http://localhost:8000';
  const key = __ENV.API_KEY || 'TEST_KEY';
  const idem = `idem-${__VU}-${__ITER__}`;

  // 1) Send event
  const ev = http.post(`${base}/v1/events`, JSON.stringify({
    type: 'login', actor_user_id: `u${__VU}`, device_hash: `d${__VU}`,
    payload: { iter: __ITER__ }
  }), {
    headers: { 'Content-Type': 'application/json', 'X-API-Key': key, 'X-Idempotency-Key': idem }
  });

  // 2) Optionally decide (auto-score if no score provided)
  if (ev.status === 200) {
    const eventId = ev.json('event_id');
    const dec = http.post(`${base}/v1/decisions`, JSON.stringify({
      event_id: eventId, outcome: 'allow'
    }), { headers: { 'Content-Type': 'application/json', 'X-API-Key': key } });
    check(dec, { 'decision ok': r => [200, 401, 429].includes(r.status) });
  }

  check(ev, { 'event ok': r => [200, 401, 429, 413].includes(r.status) });
  sleep(0.1);
}
