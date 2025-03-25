from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)

# app.state.limiter = limiter

# @app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"message": "Trop de requêtes. Réessaie plus tard."},
    )

