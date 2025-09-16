'use client';
import { useEffect, useState } from 'react';

type Item = { at:string; source:string; kind:string; subject?:string; actor?:string; payload:any };

export default function AuditPage(){
  const [q,setQ] = useState('');
  const [items,setItems] = useState<Item[]>([]);
  const load = async () => {
    const r = await fetch(`/api/proxy/audit?q=${encodeURIComponent(q)}`, { cache:'no-store' });
    const j = await r.json();
    setItems(j.items || []);
  };
  useEffect(()=>{ load(); const id=setInterval(load,10000); return ()=>clearInterval(id); },[]);
  return (
    <main style={{padding:24}}>
      <h1>Audit Timeline</h1>
      <div style={{display:'flex',gap:8,marginBottom:12}}>
        <input placeholder="search: release, flag, incident…" value={q} onChange={e=>setQ(e.target.value)} />
        <button onClick={load}>Search</button>
      </div>
      <table style={{width:'100%',borderCollapse:'collapse'}}>
        <thead><tr><th>Time</th><th>Source</th><th>Kind</th><th>Subject</th><th>Actor</th><th>Payload</th></tr></thead>
        <tbody>
          {items.map((it,idx)=>(
            <tr key={idx}>
              <td>{new Date(it.at).toLocaleString()}</td>
              <td>{it.source}</td><td>{it.kind}</td>
              <td>{it.subject||''}</td><td>{it.actor||''}</td>
              <td><code style={{fontSize:12}}>{JSON.stringify(it.payload)}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
