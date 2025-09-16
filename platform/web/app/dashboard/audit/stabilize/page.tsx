'use client';
import { useState } from 'react';

export default function StabilizePage(){
  const [state,setState] = useState<string>('idle');
  const call = async (action:'enter'|'exit')=>{
    setState('…');
    const r = await fetch('/api/proxy/stabilize', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ action }) });
    const j = await r.json();
    setState(JSON.stringify(j));
  };
  return (
    <main style={{padding:24, display:'grid', gap:12}}>
      <h1>Stabilize Mode</h1>
      <div style={{display:'flex', gap:8}}>
        <button onClick={()=>call('enter')}>Enter Stabilize</button>
        <button onClick={()=>call('exit')}>Exit Stabilize</button>
      </div>
      <pre style={{background:'#f8fafc',padding:12,borderRadius:8}}>{state}</pre>
      <p style={{color:'#64748b'}}>When enabled: RPS clamped, circuit breakers tighten, non-critical queues de-prioritized. All changes are audited.</p>
    </main>
  );
}
