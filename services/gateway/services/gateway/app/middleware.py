"""
Middleware de Argus Gateway.

RateLimitMiddleware — limita requests por API key via Redis.
LoggingMiddleware   — loguea cada request con structlog.
"""
import time
import os
from typing import Callable

import redis.asyncio as aioredis
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger()

RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = await aioredis.from_url(
                os.environ.get("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True,
            )
        return self._redis

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Saltear rate limit en health checks
        if request.url.path == "/health":
            return await call_next(request)

        api_key = request.headers.get("X-Argus-API-Key", "anonymous")
        redis = await self._get_redis()

        key = f"ratelimit:{api_key}:{int(time.time() // 60)}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)

        if count > RATE_LIMIT:
            return Response(
                content='{"detail": "Rate limit exceeded. Max 60 requests/minute."}',
                status_code=429,
                media_type="application/json",
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT - count))
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            api_key=request.headers.get("X-Argus-API-Key", "anonymous")[:8] + "...",
        )
        return response