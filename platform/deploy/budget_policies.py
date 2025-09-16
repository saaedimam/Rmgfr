from fastapi import Request
from .incident.router import open_incident, add_event
import os, asyncio

# Policy thresholds (tune in env)
P_LAT_MS = int(os.getenv("POLICY_P999_MS", "400"))
P_ERR_RATE = float(os.getenv("POLICY_ERR_RATE", "0.01"))
AUTO_ROLLBACK = os.getenv("AUTO_ROLLBACK", "true").lower() == "true"

async def enforce_policies(request: Request, snapshots):
    # if any endpoint breaks both latency and error thresholds → open or append incident and trigger rollback
    broken = [s for s in snapshots if s["latency_p99_9"] and s["latency_p99_9"] > P_LAT_MS and s["error_rate"] > P_ERR_RATE]
    if not broken: return
    key = request.headers.get("x-api-key") or os.getenv("POLICY_API_KEY","")
    if not key: return
    # open incident
    inc = await open_incident(request, type("Obj",(object,),{"severity":"SEV2","title":"Budget burn auto-detect","commander":"Auto","summary":str(broken)})())
    await add_event(request, type("Obj",(object,),{"incident_id":inc["id"],"kind":"budget_violation","payload":{"broken":broken}})())
    if AUTO_ROLLBACK:
        from .scripts.rollback import trigger_rollback
        await trigger_rollback(inc["id"], broken)
