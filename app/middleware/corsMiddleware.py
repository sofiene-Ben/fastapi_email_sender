from fastapi.responses import JSONResponse
from fastapi import Request
from app.config.app import Settings

# @app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/send-email/":
        api_key = request.headers.get("X-API-KEY")
        if not api_key or api_key != Settings.api_key:
            return JSONResponse(status_code=403, content={"detail": "Clé API invalide"})
    return await call_next(request)

