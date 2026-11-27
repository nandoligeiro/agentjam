"""Local-only API gate. Not an OS sandbox or corporate IAM substitute."""
import hmac
import logging
import os
import re
from fastapi import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("agentjam.audit")
_HOSTS = {"127.0.0.1", "127.0.0.1:8000", "127.0.0.1:5173",
          "127.0.0.1:4173", "localhost", "localhost:8000",
          "localhost:5173", "localhost:4173"}
_ORIGINS = {"http://" + host for host in _HOSTS}

def configured_token():
    token = os.getenv("AGENTJAM_API_TOKEN", "")
    if token and not re.fullmatch(r"[A-Za-z0-9_-]{43,128}", token):
        raise ValueError("AGENTJAM_API_TOKEN must be a random URL-safe token (43–128 characters)")
    return token

def pre_mode():
    mode = os.getenv("AGENTJAM_POC_MODE", "local")
    if mode not in ("local", "pre"):
        raise ValueError("Unknown AGENTJAM_POC_MODE")
    return mode == "pre"

def install_security(app, token):
    @app.middleware("http")
    async def secure(request: Request, call_next):
        status = 500
        try:
            # Vite preserves the local Host header; forwarded headers are not trusted.
            host = request.headers.get("host", "").lower()
            origin = request.headers.get("origin")
            if (host not in _HOSTS or (origin is not None and origin not in _ORIGINS)
                    or request.headers.get("sec-fetch-site") == "cross-site"):
                status = 403
                return JSONResponse({"detail":"Local origin required"}, status_code=status)
            auth = request.headers.get("authorization", "")
            if not token or not hmac.compare_digest(auth.encode(), ("Bearer " + token).encode()):
                status = 401
                return JSONResponse({"detail":"Local access token required"}, status_code=status,
                                    headers={"WWW-Authenticate":"Bearer", "Cache-Control":"no-store"})
            response = await call_next(request)
            status = response.status_code
            response.headers["Cache-Control"] = "no-store"
            return response
        finally:
            route = request.scope.get("route")
            # Do not record paths supplied by callers, request bodies, IDs or secrets.
            template = getattr(route, "path", "unmatched")
            method = request.method if request.method in ("GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD") else "OTHER"
            logger.info("api method=%s route=%s status=%s", method, template, status)
