"""
Tests de ArgusConfig.
"""
import os
import pytest

from argus_sdk.config import ArgusConfig


def test_config_defaults():
    config = ArgusConfig(api_key="test-key")
    assert config.gateway_url == "http://localhost:8000"
    assert config.service_name == "unknown"
    assert config.environment == "production"
    assert config.timeout == 10.0
    assert config.batch_size == 100
    assert config.debug is False


def test_config_custom_values():
    config = ArgusConfig(
        api_key="my-key",
        gateway_url="http://argus.mycompany.com",
        service_name="payment-service",
        environment="staging",
        debug=True,
    )
    assert config.api_key == "my-key"
    assert config.gateway_url == "http://argus.mycompany.com"
    assert config.service_name == "payment-service"
    assert config.environment == "staging"
    assert config.debug is True


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("ARGUS_API_KEY", "env-key")
    monkeypatch.setenv("ARGUS_GATEWAY_URL", "http://custom:8000")
    monkeypatch.setenv("ARGUS_SERVICE_NAME", "my-service")
    monkeypatch.setenv("ARGUS_ENVIRONMENT", "production")
    monkeypatch.setenv("ARGUS_DEBUG", "true")

    config = ArgusConfig.from_env()
    assert config.api_key == "env-key"
    assert config.gateway_url == "http://custom:8000"
    assert config.service_name == "my-service"
    assert config.debug is True


def test_config_from_env_missing_api_key():
    with pytest.raises(KeyError):
        # Si no hay ARGUS_API_KEY en el env, debe fallar
        if "ARGUS_API_KEY" in os.environ:
            del os.environ["ARGUS_API_KEY"]
        ArgusConfig.from_env()