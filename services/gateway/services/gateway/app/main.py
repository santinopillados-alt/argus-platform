"""
Argus Gateway — punto de entrada central de la plataforma.

Responsabilidades:
- Autenticación por API key
- Routing a microservicios
- Rate limiting
- Observabilidad de requests
"""
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware import RateLimitMiddleware, LoggingMiddleware
from app.router import router

logger = structlog.get_logger()

app = FastAPI(
    title="Argus Gateway",
    description="Central API gateway for the Argus observability platform",
    version="0.1.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Middleware personalizado ──────────────────────────────────────────────────
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "argus-gateway"}


@app.on_event("startup")
async def startup() -> None:
    logger.info("argus_gateway_started")


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("argus_gateway_stopped")