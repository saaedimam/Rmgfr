import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

RELEASE_FLAG_MAP = {
  "canary": {"beta_ui": True, "experimental_rules": True},
  "beta":   {"beta_ui": True},
  "prod":   {}
}

class ReleaseChannelFlags(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        channel = request.headers.get("x-release-channel", os.getenv("RELEASE","prod"))
        request.state.release_flags = RELEASE_FLAG_MAP.get(channel, {})
        return await call_next(request)
