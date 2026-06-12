# Deployment Information

## Public URL

https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/

## Platform

**Railway** — Docker runtime, auto-deploy từ GitHub

## Environment Variables Set

| Variable | Value |
|----------|-------|
| `ENVIRONMENT` | `production` |
| `APP_VERSION` | `1.0.0` |
| `AGENT_API_KEY` | *(set trong Railway dashboard)* |
| `DAILY_BUDGET_USD` | `5.0` |
| `RATE_LIMIT_PER_MINUTE` | `20` |

## Test Commands

### Health Check
```bash
curl https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/health
# Expected: {"status":"ok","version":"1.0.0","environment":"production",...}
```

### Readiness Check
```bash
curl https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/ready
# Expected: {"ready":true}
```

### Authentication Required (no key → 401)
```bash
curl -X POST https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Expected: 401 Unauthorized
```

### API Test (with authentication)
```bash
curl -X POST https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deployment?"}'
# Expected: {"question":"...","answer":"...","model":"gpt-4o-mini","timestamp":"..."}
```

### Rate Limiting Test (→ 429 after limit)
```bash
for i in $(seq 1 25); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/ask \
    -H "X-API-Key: YOUR_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"test $i\"}"
done
# Expected: 200 x20, then 429 x5
```

### Metrics (protected)
```bash
curl https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/metrics \
  -H "X-API-Key: YOUR_KEY"
# Expected: {"uptime_seconds":...,"total_requests":...,"daily_cost_usd":...}
```

## Screenshots

- [Railway Dashboard](screenshots/railway-dashboard.png)
- [Service Running](screenshots/service-running.png)
- [Test Results](screenshots/test-results.png)

## Architecture

```
Client
  │
  ▼
Railway Load Balancer
  │
  ▼
Docker Container (python:3.11-slim, non-root user)
  ├── FastAPI app (uvicorn, 2 workers)
  ├── API Key Auth (X-API-Key header)
  ├── Rate Limiter (20 req/min sliding window)
  ├── Cost Guard ($5/day budget)
  ├── GET /health  (liveness probe)
  ├── GET /ready   (readiness probe)
  ├── POST /ask    (agent endpoint)
  └── GET /metrics (protected)
```

## Repository

https://github.com/Mavinhloc/day12_ha-tang-cloud_va_deployment
