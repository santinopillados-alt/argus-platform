"""
ArgusClient — punto de entrada principal del SDK.

Uso básico:
    from argus_sdk import ArgusClient

    client = ArgusClient(api_key="xxx", service_name="payment-service")
    client.log("Payment processed", level="INFO", amount=99.99)
    client.metric("payment.latency", 142.5, unit="ms")

    with client.trace("process_payment"):
        result = process_payment(order)
"""
import asyncio
import threading
from typing import Any, Optional

import httpx

from argus_sdk.config import ArgusConfig
from argus_sdk.logs import LogBuffer
from argus_sdk.metrics import MetricBuffer
from argus_sdk.tracer import Tracer


class ArgusClient:
    def __init__(
        self,
        api_key: str,
        gateway_url: str = "http://localhost:8000",
        service_name: str = "unknown",
        environment: str = "production",
        debug: bool = False,
    ) -> None:
        self.config = ArgusConfig(
            api_key=api_key,
            gateway_url=gateway_url,
            service_name=service_name,
            environment=environment,
            debug=debug,
        )
        self._http = httpx.Client(
            base_url=gateway_url,
            headers={"X-Argus-API-Key": api_key},
            timeout=self.config.timeout,
        )
        self._log_buffer = LogBuffer(self.config, self._http)
        self._metric_buffer = MetricBuffer(self.config, self._http)
        self.tracer = Tracer(self.config, self._http)

        # Flush automático en background
        self._start_background_flush()

    # ── Logs ─────────────────────────────────────────────────────────────────

    def log(
        self,
        message: str,
        level: str = "INFO",
        **kwargs: Any,
    ) -> None:
        """Envía un log a Argus."""
        self._log_buffer.add(
            message=message,
            level=level,
            service=self.config.service_name,
            environment=self.config.environment,
            extra=kwargs,
        )

    def error(self, message: str, **kwargs: Any) -> None:
        self.log(message, level="ERROR", **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.log(message, level="WARNING", **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self.log(message, level="INFO", **kwargs)

    def capture_exception(self, exc: Exception, **kwargs: Any) -> None:
        """Captura una excepción y la envía como log ERROR."""
        self.log(
            message=f"{type(exc).__name__}: {exc}",
            level="ERROR",
            exception_type=type(exc).__name__,
            **kwargs,
        )

    # ── Métricas ──────────────────────────────────────────────────────────────

    def metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: Optional[dict] = None,
    ) -> None:
        """Envía una métrica a Argus."""
        self._metric_buffer.add(
            name=name,
            value=value,
            unit=unit,
            service=self.config.service_name,
            environment=self.config.environment,
            tags=tags or {},
        )

    def counter(self, name: str, value: float = 1.0, **tags: Any) -> None:
        self.metric(name, value, unit="count", tags=tags)

    def gauge(self, name: str, value: float, **tags: Any) -> None:
        self.metric(name, value, unit="gauge", tags=tags)

    def timing(self, name: str, value_ms: float, **tags: Any) -> None:
        self.metric(name, value_ms, unit="ms", tags=tags)

    # ── Traces ────────────────────────────────────────────────────────────────

    def trace(self, operation: str, **tags: Any):
        """Context manager para tracing distribuido."""
        return self.tracer.span(operation, **tags)

    # ── Flush ─────────────────────────────────────────────────────────────────

    def flush(self) -> None:
        """Fuerza el envío inmediato de todos los buffers."""
        self._log_buffer.flush()
        self._metric_buffer.flush()

    def close(self) -> None:
        """Flush final y cierra el cliente."""
        self.flush()
        self._http.clos