"""
Tests del Gateway — endpoints principales.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MASTER_KEY = "argus-dev-master-key"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "argus-gateway"


def test_list_services_requires_auth():
    response = client.get("/v1/services")
    assert response.status_code == 401


def test_list_services_with_master_key():
    response = client.get(
        "/v1/services",
        headers={"X-Argus-API-Key": MASTER_KEY},
    )
    # Los servicios están caídos en test — esperamos 200 con statuses
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "gateway" not in data  # gateway no se lista a sí mismo
    assert "watchdog" in data["services"]
    assert "log-lens" in data["services"]


def test_proxy_requires_auth():
    response = client.get("/v1/watchdog/health")
    assert response.status_code == 401


def test_proxy_unknown_service():
    response = client.get(
        "/v1/nonexistent/health",
        headers={"X-Argus-API-Key": MASTER_KEY},
    )
    assert response.status_code in (404, 503)


def test_proxy_unavailable_service_returns_503():
    response = client.get(
        "/v1/watchdog/health",
        headers={"X-Argus-API-Key": MASTER_KEY},
    )
    assert response.status_code == 503