'use client';
import { useState, useEffect } from 'react';

export default function IncidentsPage(){
  const [title,setTitle] = useState('Auto-detected budget burn');
  const [severity,setSeverity] = useState('SEV2');
  const [commander,setCommander] = useState('');
  const [log,setLog] = useState<string>('');

  const open = async ()=>{
    const r = await fetch('/api/proxy/incident', { method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ action:'open', payload:{ title, severity, commander }})
    });
    const j = await r.json();
    setLog(JSON.stringify(j,null,2));
  };

  return (
    <main style={{padding:24, display:'grid', gap:16}}>
      <h1>Incidents</h1>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
        <label>Title <input value={title} onChange={e=>setTitle(e.target.value)} /></label>
        <label>Severity
          <select value={severity} onChange={e=>setSeverity(e.target.value)}>
            <option>SEV1</option><option>SEV2</option><option>SEV3</option><option>SEV4</option>
          </select>
        </label>
        <label>Commander <input value={commander} onChange={e=>setCommander(e.target.value)} /></label>
      </div>
      <button onClick={open}>Open Incident</button>
      <pre style={{background:'#f8fafc', padding:12, borderRadius:8}}>{log}</pre>
    </main>
  );
}
