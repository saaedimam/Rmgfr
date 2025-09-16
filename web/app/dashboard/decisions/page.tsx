async function getDecisions(page=1) {
  const r = await fetch(`${process.env.NEXT_PUBLIC_BASE ?? ''}/api/proxy/decisions?page=${page}&page_size=20`, { cache: 'no-store' });
  return r.json();
}
export default async function DecisionsPage() {
  const data = await getDecisions(1);
  return (
    <main style={{padding:24}}>
      <h1>Decisions</h1>
      <table style={{width:'100%', borderCollapse:'collapse'}}>
        <thead><tr><th>ID</th><th>Event</th><th>Outcome</th><th>Score</th><th>Reasons</th><th>At</th></tr></thead>
        <tbody>
          {(Array.isArray(data)?data:[]).map((d:any)=>(
            <tr key={d.id}>
              <td style={{fontFamily:'monospace'}}>{d.id}</td>
              <td style={{fontFamily:'monospace'}}>{d.event_id}</td>
              <td>{d.outcome}</td>
              <td>{d.score ?? '-'}</td>
              <td>{Array.isArray(d.reasons)?d.reasons.join(', '):'-'}</td>
              <td>{new Date(d.decided_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
