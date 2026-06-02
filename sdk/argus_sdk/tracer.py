"""
Tracer — distributed tracing con context managers y decorators.

Uso:
    with client.trace("process_payment", order_id=123) as span:
        result = process_payment(order)
        span.set_tag("amount", result.amount)

    @client.tracer.instrument
    def process_payment(order):
        ...
"""
import time
import uuid
import threading
from contextlib import contextmanager
from typing import Any, Generator

import httpx

from argus_sdk.config import ArgusConfig

# Thread-local para propagar trace_id en el mismo thread
_local = threading.local()


class Span:
    def __init__(
        self,
        operation: str,
        trace_id: str,
        parent_id: str | None,
        service: str,
        tags: dict[str, Any],
        http: httpx.Client,
        config: ArgusConfig,
    ) -> None:
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.operation = operation
        self.service = service
        self.tags = tags
        self.start_time = time.perf_counter()
        self._http = http
        self._config = config
        self.error: str | None = None

    def set_tag(self, key: str, value: Any) -> None:
        self.tags[key] = value

    def set_error(self, exc: Exception) -> None:
        self.error = f"{type(exc).__name__}: {exc}"
        self.tags["error"] = True

    def finish(self) -> None:
        duration_ms = round((time.perf_counter() - self.start_time) * 1000, 2)
        payload = {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "operation": self.operation,
            "service": self.service,
            "duration_ms": duration_ms,
            "tags": self.tags,
            "error": self.error,
            "timestamp": time.time(),
        }
        try:
            self._http.post("/v1/tracer/spans", json=payload)
        except Exception as e:
            if self._config.debug:
                print(f"[ARGUS] Failed to send span: {e}")


class Tracer:
    def __init__(self, config: ArgusConfig, http: httpx.Client) -> None:
        self.config = config
        self._http = http

    @contextmanager
    def span(self, operation: str, **tags: Any) -> Generator[Span, None, None]:
        trace_id = getattr(_local, "trace_id", None) or str(uuid.uuid4())
        parent_id = getattr(_local, "span_id", None)

        s = Span(
            operation=operation,
            trace_id=trace_id,
            parent_id=parent_id,
            service=self.config.service_name,
            tags=tags,
            http=self._http,
            config=self.config,
        )

        _local.trace_id = trace_id
        _local.span_id = s.span_id

        try:
            yield s
        except Exception as exc:
            s.set_error(exc)
            raise
        finally:
            s.finish()
            _local.span_id = parent_id

    def instrument(self, func):
        """Decorator para instrumentar funciones automáticamente."""
        def wrapper(*args, **kwargs):
            with self.span(func.__name__):
                return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper