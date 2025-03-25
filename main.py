from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from app.config.app import Settings

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware et gestion d'erreur du rate limiting
from app.middleware.corsMiddleware import verify_api_key
from app.security.limiter import limiter, rate_limit_exceeded_handler
from app.routes.sendmail import email_router
from slowapi.errors import RateLimitExceeded

app.middleware("http")(verify_api_key)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# Ajout des routes
app.include_router(email_router)
