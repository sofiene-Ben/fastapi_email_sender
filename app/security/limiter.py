from slowapi import Limiter
# from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI


# Fonction pour récupérer l'adresse IP réelle
def custom_get_remote_address(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0]  # Récupère la première IP (celle du client réel)
    return request.client.host  # Fallback si pas d'IP dans l'en-tête


limiter = Limiter(key_func=custom_get_remote_address)

# app.state.limiter = limiter

# @app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"message": "Trop de requêtes. Réessaie plus tard."},
    )

# Fonction pour attacher l'exception handler à l'application FastAPI
def register_rate_limit_handler(app: FastAPI):
    app.state.limiter = limiter  # Associer le rate limiter à l'application
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)