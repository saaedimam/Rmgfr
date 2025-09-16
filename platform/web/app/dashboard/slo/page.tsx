'use client';
import { useEffect, useState } from 'react';

type Snap = { endpoint:string; latency_p99_9:number; error_rate:number; uptime:number; budget_remaining:number };

export default function SloPage(){
  const [snaps,setSnaps] = useState<Snap[]>([]);
  const load = async ()=>{
    const r = await fetch('/api/proxy/slo', { cache:'no-store' });
    const j = await r.json();
    setSnaps(j.snapshots || []);
  };
  useEffect(()=>{ load(); const id=setInterval(load, 10000); return ()=>clearInterval(id); },[]);
  return (
    <main style={{padding:24}}>
      <h1>SLO Dashboard (1h)</h1>
      <table style={{width:'100%', borderCollapse:'collapse'}}>
        <thead><tr><th>Endpoint</th><th>p99.9 (ms)</th><th>Error Rate</th><th>Uptime</th><th>Budget</th></tr></thead>
        <tbody>
          {snaps.map(s=>(
            <tr key={s.endpoint}>
              <td>{s.endpoint}</td>
              <td style={{color: s.latency_p99_9>400?'#dc2626':'inherit'}}>{Math.round(s.latency_p99_9||0)}</td>
              <td style={{color: s.error_rate>0.01?'#dc2626':'inherit'}}>{(s.error_rate*100).toFixed(2)}%</td>
              <td>{(s.uptime*100).toFixed(3)}%</td>
              <td>{(s.budget_remaining*100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{color:'#6b7280', marginTop:8}}>Targets: p99.9 ≤ 400ms, error &lt; 1%, uptime ≥ 99.9%</p>
    </main>
  );
}
