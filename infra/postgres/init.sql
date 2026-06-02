-- Argus Platform — Schema inicial
-- Cada servicio tiene su propio schema para aislamiento

CREATE SCHEMA IF NOT EXISTS watchdog;
CREATE SCHEMA IF NOT EXISTS observe_iq;
CREATE SCHEMA IF NOT EXISTS log_lens;
CREATE SCHEMA IF NOT EXISTS relay_sync;
CREATE SCHEMA IF NOT EXISTS alerting;
CREATE SCHEMA IF NOT EXISTS tracer;
CREATE SCHEMA IF NOT EXISTS anomaly_ml;
CREATE SCHEMA IF NOT EXISTS incident;
CREATE SCHEMA IF NOT EXISTS siem;
CREATE SCHEMA IF NOT EXISTS gateway;

-- ── Gateway — API keys ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gateway.api_keys (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash    TEXT NOT NULL UNIQUE,
    tenant_id   TEXT NOT NULL,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON gateway.api_keys (key_hash);

-- ── Watchdog — métricas de sistema ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS watchdog.metrics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service     TEXT NOT NULL,
    environment TEXT NOT NULL DEFAULT 'production',
    name        TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    unit        TEXT NOT NULL DEFAULT '',
    tags        JSONB NOT NULL DEFAULT '{}',
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_watchdog_metrics_service ON watchdog.metrics (service, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_watchdog_metrics_name ON watchdog.metrics (name, timestamp DESC);

-- ── ObserveIQ — logs ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS observe_iq.logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service     TEXT NOT NULL,
    environment TEXT NOT NULL DEFAULT 'production',
    level       TEXT NOT NULL,
    message     TEXT NOT NULL,
    extra       JSONB NOT NULL DEFAULT '{}',
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_service ON observe_iq.logs (service, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_level ON observe_iq.logs (level, timestamp DESC);

-- ── Log-Lens — análisis ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS log_lens.analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name    TEXT NOT NULL,
    severity        TEXT NOT NULL,
    root_cause      TEXT NOT NULL,
    what_happened   TEXT NOT NULL,
    immediate_actions JSONB NOT NULL DEFAULT '[]',
    prevention      JSONB NOT NULL DEFAULT '[]',
    stats           JSONB NOT NULL DEFAULT '{}',
    tokens_used     INTEGER NOT NULL DEFAULT 0,
    processing_ms   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Tracer — spans ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tracer.spans (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    span_id     TEXT NOT NULL,
    trace_id    TEXT NOT NULL,
    parent_id   TEXT,
    operation   TEXT NOT NULL,
    service     TEXT NOT NULL,
    duration_ms DOUBLE PRECISION NOT NULL,
    tags        JSONB NOT NULL DEFAULT '{}',
    error       TEXT,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_spans_trace ON tracer.spans (trace_id);
CREATE INDEX IF NOT EXISTS idx_spans_service ON tracer.spans (service, timestamp DESC);

-- ── Alerting — alertas ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alerting.alerts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service     TEXT NOT NULL,
    severity    TEXT NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    channel     TEXT NOT NULL,
    sent_at     TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerting.rules (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    condition   JSONB NOT NULL,
    channels    JSONB NOT NULL DEFAULT '[]',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Incident — incidents ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS incident.incidents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    severity    TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open',
    service     TEXT NOT NULL,
    assignee    TEXT,
    timeline    JSONB NOT NULL DEFAULT '[]',
    postmortem  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ── SIEM — eventos de seguridad ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS siem.security_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type        TEXT NOT NULL,
    severity    TEXT NOT NULL,
    source_ip   TEXT,
    service     TEXT NOT NULL,
    description TEXT NOT NULL,
    raw         JSONB NOT NULL DEFAULT '{}',
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_siem_type ON siem.security_events (type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_siem_ip ON siem.security_events (source_ip, timestamp DESC);

-- ── Anomaly ML ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anomaly_ml.anomalies (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service     TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    expected    DOUBLE PRECISION NOT NULL,
    deviation   DOUBLE PRECISION NOT NULL,
    severity    TEXT NOT NULL,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);