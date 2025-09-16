import os, time, httpx
from api.stabilize import is_stabilized

COST_LIMIT_MONTH = float(os.getenv("COST_LIMIT_MONTH","2500"))

async def check_cost_and_signal():
    # pseudo: pull costs from your billing exporter (BigQuery/Cloud API). Here we stub as env.
    cost = float(os.getenv("CURRENT_COST","0"))
    if cost > COST_LIMIT_MONTH and not is_stabilized():
        # POST to /v1/stabilize/enter via internal call or audit a warning
        pass
