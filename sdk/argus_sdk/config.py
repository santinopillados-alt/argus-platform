"""
Configuración del SDK de Argus.
"""
from dataclasses import dataclass, field
import os


@dataclass
class ArgusConfig:
    api_key: str
    gateway_url: str = "http://localhost:8000"
    service_name: str = "unknown"
    environment: str = "production"
    timeout: float = 10.0
    batch_size: int = 100
    flush_interval: float = 5.0
    debug: bool = False

    @classmethod
    def from_env(cls) -> "ArgusConfig":
        return cls(
            api_key=os.environ["ARGUS_API_KEY"],
            gateway_url=os.environ.get("ARGUS_GATEWAY_URL", "http://localhost:8000"),
            service_name=os.environ.get("ARGUS_SERVICE_NAME", "unknown"),
            environment=os.environ.get("ARGUS_ENVIRONMENT", "production"),
            debug=os.environ.get("ARGUS_DEBUG", "false").lower() == "true",
        )