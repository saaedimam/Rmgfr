async function getEvents(page=1) {
  const r = await fetch(`${process.env.NEXT_PUBLIC_BASE ?? ''}/api/proxy/events?page=${page}&page_size=20`, { cache: 'no-store' });
  return r.json();
}
export default async function EventsPage() {
  const data = await getEvents(1);
  return (
    <main style={{padding:24}}>
      <h1>Events</h1>
      <table style={{width:'100%', borderCollapse:'collapse'}}>
        <thead><tr><th>ID</th><th>Type</th><th>User</th><th>IP</th><th>Device</th><th>At</th></tr></thead>
        <tbody>
          {(Array.isArray(data)?data:[]).map((e:any)=>(
            <tr key={e.id}>
              <td style={{fontFamily:'monospace'}}>{e.id}</td>
              <td>{e.type}</td>
              <td>{e.actor_user_id ?? '-'}</td>
              <td>{e.ip ?? '-'}</td>
              <td>{e.device_hash ?? '-'}</td>
              <td>{new Date(e.event_ts).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
