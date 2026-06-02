"""
Buffer de métricas — agrupa y envía en batch para eficiencia.
"""
import threading
import time
from typing import Any

import httpx

from argus_sdk.config import ArgusConfig


class MetricBuffer:
    def __init__(self, config: ArgusConfig, http: httpx.Client) -> None:
        self.config = config
        self._http = http
        self._buffer: list[dict] = []
        self._lock = threading.Lock()

    def add(
        self,
        name: str,
        value: float,
        unit: str,
        service: str,
        environment: str,
        tags: dict[str, Any],
    ) -> None:
        entry = {
            "timestamp": time.time(),
            "name": name,
            "value": value,
            "unit": unit,
            "service": service,
            "environment": environment,
            "tags": tags,
        }

        if self.config.debug:
            print(f"[ARGUS METRIC] {name}={value}{unit}")

        with self._lock:
            self._buffer.append(entry)
            if len(self._buffer) >= self.config.batch_size:
                self._send()

    def flush(self) -> None:
        with self._lock:
            if self._buffer:
                self._send()

    def _send(self) -> None:
        """Envía el buffer al servicio watchdog via gateway. Lock debe estar tomado."""
        if not self._buffer:
            return

        batch = self._buffer.copy()
        self._buffer.clear()

        try:
            self._http.post(
                "/v1/watchdog/ingest/metrics",
                json={"metrics": batch},
            )
        except Exception as e:
            if self.config.debug:
                print(f"[ARGUS] Failed to send metrics: {e}")