"""
Router central — enruta requests a cada microservicio.
"""
import os
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.auth import validate_api_key

router = APIRouter()

# URLs de cada servicio — en producción vienen de env vars
SERVICES = {
    "watchdog":   os.environ.get("WATCHDOG_URL",   "http://watchdog-backend:8000"),
    "observe-iq": os.environ.get("OBSERVE_IQ_URL", "http://observe-iq:8000"),
    "log-lens":   os.environ.get("LOG_LENS_URL",   "http://log-lens:8000"),
    "relay-sync": os.environ.get("RELAY_SYNC_URL", "http://relay-sync:8000"),
    "alerting":   os.environ.get("ALERTING_URL",   "http://alerting:8000"),
    "tracer":     os.environ.get("TRACER_URL",      "http://tracer:8000"),
    "anomaly-ml": os.environ.get("ANOMALY_ML_URL", "http://anomaly-ml:8000"),
    "incident":   os.environ.get("INCIDENT_URL",   "http://incident:8000"),
    "siem":       os.environ.get("SIEM_URL",        "http://siem:8000"),
}


async def _proxy(
    service: str,
    request: Request,
    path: str,
    tenant_id: str,
) -> Response:
    """Proxy genérico — reenvía el request al servicio destino."""
    base_url = SERVICES.get(service)
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service}' not found.",
        )

    url = f"{base_url}/{path}"
    body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers={
                    "X-Argus-Tenant": tenant_id,
                    "Content-Type": request.headers.get("Content-Type", "application/json"),
                },
                content=body,
                params=dict(request.query_params),
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service '{service}' is unavailable.",
            )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )


# ── Rutas por servicio ────────────────────────────────────────────────────────

@router.api_route(
    "/v1/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy(
    service: str,
    path: str,
    request: Request,
    tenant_id: Annotated[str, Depends(validate_api_key)],
) -> Response:
    return await _proxy(service, request, path, tenant_id)


@router.get("/v1/services")
async def list_services(
    tenant_id: Annotated[str, Depends(validate_api_key)],
) -> dict:
    """Lista todos los servicios disponibles y su estado."""
    statuses = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(f"{url}/health")
                statuses[name] = "healthy" if r.status_code == 200 else "degraded"
            except Exception:
                statuses[name] = "unavailable"
    return {"services": statuses}