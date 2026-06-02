# Argus — Open-Source Observability Platform

> Self-hostable alternative to Datadog. Metrics, logs, traces, alerts, AI analysis, and security — in one stack.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-7.5-black)](https://kafka.apache.org)

## What is Argus?

Argus is a production-grade observability platform you can run on your own infrastructure. Connect any application in 3 lines of Python and get full visibility into your systems — without paying $15/host/month.

```python
from argus_sdk import ArgusClient

client = ArgusClient(api_key="xxx", service_name="payment-service")
client.info("Payment processed", amount=99.99, user_id=123)
client.metric("payment.latency", 142.5, unit="ms")
```

## Architecture
## Services

| Service | Description | Port |
|---|---|---|
| **gateway** | Central API gateway — auth, routing, rate limiting | 8000 |
| **watchdog** | Real-time system metrics — CPU, RAM, disk | 8001 |
| **observe-iq** | Log pipeline via Apache Kafka | 8002 |
| **log-lens** | AI-powered root cause analysis (Claude API) | 8003 |
| **relay-sync** | PostgreSQL CDC replication via WAL | 8004 |
| **alerting** | Multi-channel alerting — Slack, email, PagerDuty | 8005 |
| **tracer** | Distributed tracing with flame graphs | 8006 |
| **anomaly-ml** | ML-based anomaly detection | 8007 |
| **incident** | Incident management + auto postmortem | 8008 |
| **siem** | Security event detection + compliance reports | 8009 |
| **dashboard** | Unified React frontend | 3000 |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/santinopillados-alt/argus-platform
cd argus-platform

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run
docker-compose up
```

Visit `http://localhost` for the dashboard and `http://localhost:8000/docs` for the API.

## SDK

```bash
pip install argus-sdk
```

```python
from argus_sdk import ArgusClient

client = ArgusClient(
    api_key="your-api-key",
    service_name="my-service",
    environment="production",
)

# Logs
client.info("User logged in", user_id=123)
client.error("Payment failed", order_id=456, amount=99.99)
client.capture_exception(exc)

# Metrics
client.metric("api.latency", 142.5, unit="ms")
client.counter("requests.total")
client.gauge("queue.depth", 42)

# Traces
with client.trace("process_payment", order_id=123) as span:
    result = process_payment(order)
    span.set_tag("amount", result.amount)
```

## Stack

- **Language:** Python 3.12
- **API:** FastAPI + asyncpg
- **Message broker:** Apache Kafka
- **Database:** PostgreSQL 17
- **Cache:** Redis 7
- **AI:** Anthropic Claude API
- **Frontend:** React 18 + TypeScript
- **Infra:** Docker + Nginx

## Status

| Component | Status |
|---|---|
| Gateway | ✅ Complete |
| SDK | ✅ Complete |
| Watchdog | 🔄 Migrating |
| ObserveIQ | 🔄 Migrating |
| Log-Lens | 🔄 Migrating |
| Relay-Sync | 🔄 Migrating |
| Alerting | 🚧 In progress |
| Tracer | 🚧 In progress |
| Anomaly-ML | 🚧 In progress |
| Incident | 🚧 In progress |
| SIEM | 🚧 In progress |
| Dashboard | 🚧 In progress |

## Author

**Santino Coronel** — Self-taught backend engineer from Argentina.
Relocating to Portugal mid-2027.

[GitHub](https://github.com/santinopillados-alt) · [Contra](https://contra.com/santino_coronel_2nuzllll)