import Constants from 'expo-constants';

const base = (Constants?.expoConfig?.extra as any)?.mobileProxyBase || 'http://localhost:3000';

export async function pingHealth() {
  const r = await fetch(`${base}/api/mobile/health`, { method:'GET' });
  if (!r.ok) throw new Error('health failed');
  return r.json();
}

export async function postMobileEvent(body: any) {
  const r = await fetch(`${base}/api/mobile/events`, {
    method:'POST',
    headers: {
      'Content-Type':'application/json',
      'X-Idempotency-Key': `mob-${Date.now()}-${Math.random()}`
    },
    body: JSON.stringify(body)
  });
  return r.json();
}
