async function getEvents(page=1) {
  const r = await fetch(`${process.env.NEXT_PUBLIC_BASE ?? ''}/api/proxy/events?page=${page}&page_size=20`, { cache: 'no-store' });
  return r.json();
}
export default async function EventsPage() {
  const data = await getEvents(1);
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Events</h1>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="border border-gray-300 px-4 py-2 text-left">ID</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Type</th>
              <th className="border border-gray-300 px-4 py-2 text-left">User</th>
              <th className="border border-gray-300 px-4 py-2 text-left">IP</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Device</th>
              <th className="border border-gray-300 px-4 py-2 text-left">At</th>
            </tr>
          </thead>
          <tbody>
            {(Array.isArray(data)?data:[]).map((e:any)=>(
              <tr key={e.id} className="hover:bg-gray-50">
                <td className="border border-gray-300 px-4 py-2 font-mono text-sm">{e.id}</td>
                <td className="border border-gray-300 px-4 py-2">{e.type}</td>
                <td className="border border-gray-300 px-4 py-2">{e.actor_user_id ?? '-'}</td>
                <td className="border border-gray-300 px-4 py-2">{e.ip ?? '-'}</td>
                <td className="border border-gray-300 px-4 py-2">{e.device_hash ?? '-'}</td>
                <td className="border border-gray-300 px-4 py-2 text-sm">{new Date(e.event_ts).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
