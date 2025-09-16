'use client';
import { useEffect, useState } from 'react';

type Flag = { id:string; key:string; enabled:boolean; description?:string; updated_at:string };

export default function FlagsPage() {
  const [projectId, setProjectId] = useState('');
  const [flags, setFlags] = useState<Flag[]>([]);
  const [key, setKey] = useState('beta_ui');
  const [desc, setDesc] = useState('Enable beta UI');
  const [enabled, setEnabled] = useState(false);
  const [status, setStatus] = useState('');

  const load = async () => {
    if (!projectId) return;
    setStatus('Loading…');
    const r = await fetch(`/api/proxy/flags?project_id=${projectId}`);
    const data = await r.json();
    setFlags(Array.isArray(data) ? data : []);
    setStatus('');
  };

  const upsert = async () => {
    if (!projectId) { setStatus('Project ID required'); return; }
    setStatus('Saving…');
    const r = await fetch('/api/proxy/flags', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({ project_id: projectId, key, enabled, description: desc })
    });
    setStatus(r.ok ? 'Saved ✓' : `Error ${r.status}`);
    await load();
  };

  useEffect(()=>{ /* no-op */ },[]);

  return (
    <main style={{ padding:24, display:'grid', gap:16, maxWidth:900 }}>
      <h1>Feature Flags</h1>

      <label>Project ID
        <input value={projectId} onChange={e=>setProjectId(e.target.value)} placeholder="UUID" style={{ width:'100%' }}/>
      </label>

      <button onClick={load} style={{width:160}}>Load Flags</button>

      <section style={{border:'1px solid #ddd', borderRadius:8, padding:12}}>
        <h3>Create / Update Flag</h3>
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
          <label>key <input value={key} onChange={e=>setKey(e.target.value)} /></label>
          <label>description <input value={desc} onChange={e=>setDesc(e.target.value)} /></label>
          <label>enabled <input type="checkbox" checked={enabled} onChange={e=>setEnabled(e.target.checked)} /></label>
        </div>
        <button onClick={upsert} style={{marginTop:12}}>Save</button>
      </section>

      <section>
        <h3>Flags</h3>
        <table style={{width:'100%', borderCollapse:'collapse'}}>
          <thead><tr><th>Key</th><th>Enabled</th><th>Description</th><th>Updated</th></tr></thead>
          <tbody>
            {flags.map(f=>(
              <tr key={f.id}>
                <td>{f.key}</td>
                <td>{f.enabled ? '✓' : '—'}</td>
                <td>{f.description ?? '-'}</td>
                <td>{new Date(f.updated_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <p style={{color:'#555'}}>{status}</p>
    </main>
  );
}
