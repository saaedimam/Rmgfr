'use client';
import Link from 'next/link';
import { UserButton } from '@clerk/nextjs';

export default function Nav() {
  return (
    <header style={{display:'flex', justifyContent:'space-between', padding:'12px 16px', borderBottom:'1px solid #e5e7eb'}}>
      <nav style={{display:'flex', gap:12}}>
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/dashboard/events">Events</Link>
        <Link href="/dashboard/decisions">Decisions</Link>
        <Link href="/dashboard/rules">Rules</Link>
        <Link href="/dashboard/flags">Flags</Link>
        <Link href="/dashboard/incidents">Incidents</Link>
        <Link href="/dashboard/slo">SLO</Link>
        <Link href="/dashboard/audit">Audit</Link>
      </nav>
      <UserButton afterSignOutUrl="/sign-in" />
    </header>
  );
}
