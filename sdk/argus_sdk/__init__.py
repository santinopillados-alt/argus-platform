"""
Argus SDK — conectá tu app a la plataforma Argus en 3 líneas.

    from argus_sdk import ArgusClient

    client = ArgusClient(api_key="xxx", service_name="my-service")
    client.info("Server started")
    client.metric("requests.count", 1)
"""
from argus_sdk.client import ArgusClient
from argus_sdk.config import ArgusConfig

__all__ = ["ArgusClient", "ArgusConfig"]
__version__ = "0.1.0"