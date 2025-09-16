import os, subprocess, asyncio, json

VERCEL_TOKEN = os.getenv("VERCEL_TOKEN","")
VERCEL_PROJECT = os.getenv("VERCEL_PROJECT","")
VERCEL_TEAM = os.getenv("VERCEL_TEAM","")
FLY_APP = os.getenv("FLY_APP","")
RENDER_SERVICE_ID = os.getenv("RENDER_SERVICE_ID","")
RENDER_API_KEY = os.getenv("RENDER_API_KEY","")

async def _run(cmd: list[str]) -> tuple[int,str]:
    p = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    out,_ = await p.communicate()
    return p.returncode, out.decode()

async def rollback_vercel():
    if not (VERCEL_TOKEN and VERCEL_PROJECT): return "vercel:skipped"
    # Use Vercel CLI via API: switch prod alias to previous deployment
    # Requires vercel CLI installed in runner image or use REST API (omitted token security)
    return "vercel:manual-recommended"  # keep CLI/API token handling off here

async def rollback_fly():
    if not FLY_APP: return "fly:skipped"
    code, out = await _run(["flyctl","releases","list","-a",FLY_APP,"--json"])
    if code != 0: return f"fly:error:{out}"
    rel = json.loads(out)
    if len(rel) < 2: return "fly:no_previous_release"
    prev = rel[1]["version"]
    code, out = await _run(["flyctl","releases","rollback","-a",FLY_APP,str(prev)])
    return "fly:" + ("ok" if code==0 else f"err:{out}")

async def rollback_render():
    if not (RENDER_API_KEY and RENDER_SERVICE_ID): return "render:skipped"
    # Render supports deploys from latest build; emulate rollback by re-deploying previous build via API (pseudo)
    return "render:manual-recommended"

async def trigger_rollback(incident_id: str, broken):
    results = []
    r = await rollback_fly()
    results.append(r)
    r2 = await rollback_vercel()
    results.append(r2)
    r3 = await rollback_render()
    results.append(r3)
    # TODO: write to incident_events via API call (avoid circular import)
    print(f"[rollback] incident={incident_id} results={results} broken={broken}")
