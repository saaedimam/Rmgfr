import Link from 'next/link';

export default function Home() {
  return (
    <main style={{padding:24}}>
      <h1>Platform Dashboard</h1>
      <p><Link href="/sign-in">Sign in</Link> to access your dashboard.</p>
    </main>
  );
}
