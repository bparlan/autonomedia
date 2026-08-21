# Deployment Guide

| Property | Value |
|----------|-----|
| Document Type | Deployment Guide |
| Derived From | M15S4 |
| Version | 1.0 |

---

## Deployment Architecture Overview

Autonomedia uses a containerized deployment architecture with the following components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer                            │
└─────────────────────┬─────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼───────┐       ┌─────────▼─────────┐
│   Primary     │       │   Backup/Standby  │
│   Instance    │       │   Instance        │
│               │       │                   │
│ - Publishing  │       │ - Standby         │
│ - Monitoring  │       │ - Monitoring      │
│ - Reauth      │       │ - Reauth          │
└───────────────┘       └───────────────────┘
```

### Components

| Component | Description | Scaling |
|-----------|-------------|---------|
| Browser Provider | Manages anti-detection browser instances | Horizontal |
| Publishing Routine | Core publishing scheduler and queue | Horizontal |
| Platform Handlers | LinkedIn/X/Mastodon API clients | 1 per platform |
| Reauth Manager | Authentication lifecycle | Single active |
| Monitoring | Metrics, alerts, dashboards | Single/active-active |

---

## Configuration Requirements

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LINKEDIN_AUTH_TOKEN` | LinkedIn API access token | Yes |
| `X_AUTH_TOKEN` | X (Twitter) API access token | Yes |
| `MASTODON_AUTH_TOKEN` | Mastodon API access token | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis queue connection | Yes |
| `SLACK_WEBHOOK_URL` | Slack alert webhook | For alerts |
| `EMAIL_SMTP_HOST` | SMTP host for alerts | For email alerts |
| `LOG_LEVEL` | Logging verbosity (DEBUG/INFO/WARNING) | No (default: INFO) |

### Secrets Management

Tokens are stored in environment variables. For production deployments:

```bash
# Using Docker secrets
echo "your-linkedin-token" > /run/secrets/linkedin_token
echo "your-x-token" > /run/secrets/x_token
echo "your-mastodon-token" > /run/secrets/mastodon_token
```

---

## Environment Setup Instructions

### Prerequisites

- Docker 24.0+
- Docker Compose 2.0+
- 2GB RAM minimum (4GB recommended)
- Network access to platform APIs

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/autonomedia/autonomedia.git
cd autonomedia

# 2. Set environment variables
cp .env.example .env
# Edit .env with your tokens

# 3. Start services
docker compose up -d

# 4. Verify health
curl http://localhost:8000/health
```

### Production Setup

```bash
# 1. Create secrets
./scripts/setup_secrets.sh

# 2. Pull images
docker compose -f docker-compose.prod.yml pull

# 3. Start with production config
docker compose -f docker-compose.prod.yml up -d

# 4. Wait for readiness
./scripts/wait_for_ready.sh
```

---

## Platform-Specific Deployment Steps

### LinkedIn

- Uses OAuth 2.0 with anti-detection browser
- Requires valid LinkedIn Developer App credentials
- Token refresh every 60 days

```bash
# Check LinkedIn status
docker compose exec autonomedia python reauth_script.py --platform linkedin --check
```

### X (Twitter)

- Uses OAuth 2.0 Bearer token
- Requires Twitter Developer API access
- Monitor rate limit headers (300 posts/3hr)

```bash
# Check X status
docker compose exec autonomedia python reauth_script.py --platform x --check
```

### Mastodon

- Uses OAuth 2.0 with instance-specific tokens
- Works with any Mastodon-compatible instance
- No strict rate limits (polite usage recommended)

```bash
# Check Mastodon status
docker compose exec autonomedia python reauth_script.py --platform mastodon --check
```

---

## Health Checks and Readiness Probes

### Endpoints

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/health` | Overall system health | `{"status": "healthy", "checks": {...}}` |
| `/ready` | Readiness for traffic | `{"status": "ready", "checks": {...}}` |
| `/live` | Liveness probe | `{"status": "alive", "uptime": ...}` |
| `/metrics` | Prometheus metrics | Text/plain metrics |

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## Zero-Downtime Update Procedures

### Rolling Deployment Strategy

1. Deploy new instance to staging
2. Validate with canary traffic (10%)
3. Monitor health checks for 5 minutes
4. Gradually roll to 100% over 10 minutes

### Update Script

```bash
# ./scripts/run_production.py update
# Performs:
# 1. Health check before update
# 2. Pull new images
# 3. Rolling update of services
# 4. Validate health after update
# 5. Rollback on failure
```

### Rollback Procedure

```bash
# Automatic rollback triggered by:
# - Health check failure
# - Success rate drop <80%
# - Authentication failure rate >50%

# Manual rollback
./scripts/run_production.py rollback
```

---

## Pre-Deployment Checklist

- [ ] Tokens validated and not expired
- [ ] Database migrations applied
- [ ] Redis queue accessible
- [ ] Network connectivity to all platforms
- [ ] Alerting channels configured
- [ ] Logging infrastructure ready
- [ ] Backup strategy verified

---

## Post-Deployment Validation

- [ ] All health endpoints responding
- [ ] Platform handlers authenticated
- [ ] Publishing queue processing
- [ ] Monitoring dashboards active
- [ ] Alert webhooks tested
- [ ] Log aggregation working