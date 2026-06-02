"""
Tests de autenticación del Gateway.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MASTER_KEY = "argus-dev-master-key"


def test_missing_api_key_returns_401():
    response = client.get("/v1/services")
    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]


def test_invalid_api_key_returns_401():
    response = client.get(
        "/v1/services",
        headers={"X-Argus-API-Key": "invalid-key-xyz"},
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


def test_master_key_is_accepted():
    response = client.get(
        "/v1/services",
        headers={"X-Argus-API-Key": MASTER_KEY},
    )
    assert response.status_code == 200


def test_empty_api_key_returns_401():
    response = client.get(
        "/v1/services",
        headers={"X-Argus-API-Key": ""},
    )
    assert response.status_code == 401