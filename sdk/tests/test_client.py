"""
Tests del ArgusClient SDK.
"""
import pytest
from unittest.mock import MagicMock, patch

from argus_sdk import ArgusClient
from argus_sdk.config import ArgusConfig


@pytest.fixture
def client():
    with patch("httpx.Client") as mock_http:
        mock_http.return_value = MagicMock()
        c = ArgusClient(
            api_key="test-key",
            service_name="test-service",
            environment="test",
            debug=True,
        )
        yield c
        c._http.close()


def test_client_initializes(client):
    assert client.config.api_key == "test-key"
    assert client.config.service_name == "test-service"
    assert client.config.environment == "test"


def test_log_adds_to_buffer(client):
    client.log("Test message", level="INFO")
    assert len(client._log_buffer._buffer) == 1
    entry = client._log_buffer._buffer[0]
    assert entry["message"] == "Test message"
    assert entry["level"] == "INFO"
    assert entry["service"] == "test-service"


def test_error_shortcut(client):
    client.error("Something failed")
    entry = client._log_buffer._buffer[0]
    assert entry["level"] == "ERROR"


def test_warning_shortcut(client):
    client.warning("Something suspicious")
    entry = client._log_buffer._buffer[0]
    assert entry["level"] == "WARNING"


def test_info_shortcut(client):
    client.info("All good")
    entry = client._log_buffer._buffer[0]
    assert entry["level"] == "INFO"


def test_capture_exception(client):
    try:
        raise ValueError("test error")
    except ValueError as e:
        client.capture_exception(e)
    entry = client._log_buffer._buffer[0]
    assert entry["level"] == "ERROR"
    assert "ValueError" in entry["message"]


def test_metric_adds_to_buffer(client):
    client.metric("cpu.usage", 42.5, unit="%")
    assert len(client._metric_buffer._buffer) == 1
    entry = client._metric_buffer._buffer[0]
    assert entry["name"] == "cpu.usage"
    assert entry["value"] == 42.5
    assert entry["unit"] == "%"


def test_counter_shortcut(client):
    client.counter("requests.total")
    entry = client._metric_buffer._buffer[0]
    assert entry["unit"] == "count"
    assert entry["value"] == 1.0


def test_gauge_shortcut(client):
    client.gauge("queue.depth", 42)
    entry = client._metric_buffer._buffer[0]
    assert entry["unit"] == "gauge"
    assert entry["value"] == 42


def test_timing_shortcut(client):
    client.timing("api.latency", 142.5)
    entry = client._metric_buffer._buffer[0]
    assert entry["unit"] == "ms"
    assert entry["value"] == 142.5


def test_flush_clears_buffers(client):
    client.info("test")
    client.metric("test.metric", 1.0)
    client.flush()
    assert len(client._log_buffer._buffer) == 0
    assert len(client._metric_buffer._buffer) == 0


def test_context_manager(client):
    with client as c:
        c.info("inside context")
    # No debe lanzar excepciones al cerrar