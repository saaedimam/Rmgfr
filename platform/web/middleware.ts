import { NextResponse, NextRequest } from 'next/server';
const ALLOW_CIDRS = (process.env.ALLOW_CIDRS || '').split(',').filter(Boolean);
const DENY_IPS = (process.env.DENY_IPS || '').split(',').filter(Boolean);

function ip(req: NextRequest){ return req.ip ?? req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? '';}
function prefix(ip: string, cidr: string){ const [block, bits] = cidr.split('/'); return ip.startsWith(block.split('.').slice(0, Number(bits)/8).join('.')); }

export const config = { matcher: ['/((?!_next|static|favicon.ico).*)'] };

const buckets = new Map<string,{t:number,c:number}>(); // in-memory edge minute bucket

export async function middleware(req: NextRequest) {
  const client = ip(req);
  if (DENY_IPS.includes(client)) return new NextResponse('blocked', { status: 403 });
  if (ALLOW_CIDRS.length && !ALLOW_CIDRS.some(c=>prefix(client,c))) return new NextResponse('forbidden', { status: 403 });

  // soft rate limit: per IP per minute by path class
  const key = `${client}:${req.nextUrl.pathname.split('/')[1] || 'root'}`;
  const now = Date.now(); const entry = buckets.get(key) || { t: now, c: 0 };
  if (now - entry.t > 60_000) { entry.t = now; entry.c = 0; }
  entry.c++; buckets.set(key, entry);
  const LIMIT = req.nextUrl.pathname.startsWith('/api') ? 600 : 1200; // tune
  if (entry.c > LIMIT) return new NextResponse('rate-limited', { status: 429 });

  // security headers
  const res = NextResponse.next();
  res.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  res.headers.set('Content-Security-Policy', "default-src 'self' https: 'unsafe-inline' 'unsafe-eval'");
  res.headers.set('X-Content-Type-Options', 'nosniff');
  res.headers.set('X-Frame-Options', 'DENY');
  res.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  return res;
}
