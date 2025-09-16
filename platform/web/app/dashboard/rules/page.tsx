'use client';
import { useState } from 'react';

export default function RulesPage() {
  const [projectId, setProjectId] = useState('');
  const [form, setForm] = useState({
    max_events_per_ip: 60,
    max_events_per_user: 60,
    max_events_per_device: 120,
    max_events_global: 5000,
    window_seconds: 300
  });
  const [status, setStatus] = useState<string>('');

  const onChange = (k: string, v: number) => setForm(f => ({ ...f, [k]: v }));

  const submit = async () => {
    setStatus('Saving…');
    const r = await fetch('/api/proxy/rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, ...form })
    });
    setStatus(r.ok ? 'Saved ✓' : `Error (${r.status})`);
  };

  return (
    <main style={{ padding: 24, display: 'grid', gap: 16, maxWidth: 720 }}>
      <h1>Rules Configuration</h1>
      <label>Project ID
        <input value={projectId} onChange={e=>setProjectId(e.target.value)} placeholder="UUID" style={{ width:'100%' }}/>
      </label>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
        <label>Max / IP (5m)<input type="number" value={form.max_events_per_ip} onChange={e=>onChange('max_events_per_ip', +e.target.value)}/></label>
        <label>Max / User (5m)<input type="number" value={form.max_events_per_user} onChange={e=>onChange('max_events_per_user', +e.target.value)}/></label>
        <label>Max / Device (5m)<input type="number" value={form.max_events_per_device} onChange={e=>onChange('max_events_per_device', +e.target.value)}/></label>
        <label>Max Global (5m)<input type="number" value={form.max_events_global} onChange={e=>onChange('max_events_global', +e.target.value)}/></label>
        <label>Window (sec)<input type="number" value={form.window_seconds} onChange={e=>onChange('window_seconds', +e.target.value)}/></label>
      </div>

      <button onClick={submit} style={{ padding: '8px 14px' }}>Save</button>
      <p>{status}</p>

      <section style={{ fontSize: 12, color: '#555' }}>
        <strong>Notes:</strong> Changes affect **new** requests within the rolling window. This proxy uses a **server-side ADMIN_TOKEN**.
      </section>
    </main>
  );
}
