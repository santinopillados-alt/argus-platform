"""
Autenticación por API key para Argus Gateway.

Cada tenant tiene una API key única.
Las keys se validan contra Redis para performance.
"""
import hashlib
import os
from typing import Optional

import redis.asyncio as aioredis
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-Argus-API-Key", auto_error=False)

MASTER_KEY = os.environ.get("ARGUS_MASTER_KEY", "argus-dev-master-key")

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True,
        )
    return _redis


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


async def validate_api_key(
    api_key: str = Security(API_KEY_HEADER),
) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-Argus-API-Key header.",
        )

    # Master key para desarrollo — nunca en producción
    if api_key == MASTER_KEY:
        return "master"

    redis = await get_redis()
    key_hash = _hash_key(api_key)
    tenant_id = await redis.get(f"apikey:{key_hash}")

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return tenant_id