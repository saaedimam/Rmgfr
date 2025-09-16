import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '1m',
  thresholds: {
    http_req_duration: ['p(99.9)<400'],
  },
};

export default function () {
  const url = __ENV.API_BASE || 'http://localhost:8000/v1/events';
  const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': __ENV.API_KEY || 'TEST_KEY',
    'X-Idempotency-Key': `idem-${__VU}-${__ITER__}`
  };
  const payload = JSON.stringify({ type: 'login', payload: { u: '1' }});
  const res = http.post(url, payload, { headers });
  check(res, { 'accepted or authed?': (r) => [200,401,429,413].includes(r.status) });
  sleep(0.5);
}
