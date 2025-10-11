from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from app.config.app import Settings
from app.middleware.corsMiddleware import verify_api_key
from app.security.limiter import limiter, rate_limit_exceeded_handler, register_rate_limit_handler
from app.routes.sendmail import email_router

app = FastAPI(
    title="mail sender",
    description="API pour envoyer des emails",
    version="1.0",
    docs_url="/docs" if Settings.debug else None,  # Swagger UI
    redoc_url="/redoc" if Settings.debug else None,  # ReDoc
    openapi_url="/openapi.json" if Settings.debug else None  # OpenAPI JSON
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
# app.middleware("http")(verify_api_key)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

register_rate_limit_handler(app)

# Ajout des routes
app.include_router(email_router)