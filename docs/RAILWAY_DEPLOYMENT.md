# CardioGuard AI — Railway Deployment Guide

> **Disclaimer:** CardioGuard AI is a general wellness and lifestyle monitoring platform. Not a medical device. Always consult a qualified healthcare provider for clinical decisions.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1 — Create a Railway Project](#step-1--create-a-railway-project)
4. [Step 2 — Provision Databases](#step-2--provision-databases)
5. [Step 3 — Deploy the API Gateway](#step-3--deploy-the-api-gateway)
6. [Step 4 — Deploy the Wellness Engine](#step-4--deploy-the-wellness-engine)
7. [Step 5 — Configure Environment Variables](#step-5--configure-environment-variables)
8. [Step 6 — Service Networking](#step-6--service-networking)
9. [Step 7 — Database Initialisation](#step-7--database-initialisation)
10. [Step 8 — Health Checks & Monitoring](#step-8--health-checks--monitoring)
11. [Step 9 — Custom Domains](#step-9--custom-domains)
12. [Troubleshooting](#troubleshooting)

---

## Overview

CardioGuard AI deploys as **five Railway services** within a single project:

| Railway Service | Source | Internal Port |
|---|---|---|
| `api-gateway` | `backend/api-gateway/` | 3000 |
| `wellness-engine` | `backend/app/` | 8000 |
| `postgres` | Railway Plugin | 5432 |
| `redis` | Railway Plugin | 6379 |
| `influxdb` | Railway Plugin (or Docker image) | 8086 |

All services communicate over Railway's private network using internal hostnames (e.g. `postgres.railway.internal`). Only `api-gateway` is exposed to the public internet.

---

## Prerequisites

- A [Railway](https://railway.app) account (Hobby plan or above recommended for production)
- The CardioGuard AI repository pushed to GitHub
- Railway CLI installed (optional but useful): `npm install -g @railway/cli`

---

## Step 1 — Create a Railway Project

1. Log in to [railway.app](https://railway.app) and click **New Project**.
2. Select **Deploy from GitHub repo** and authorise Railway to access your GitHub account.
3. Choose the `CardioGuardAI` repository.
4. Railway will detect the repository — click **Add service** to continue (do not auto-deploy yet).

---

## Step 2 — Provision Databases

### PostgreSQL

1. In your Railway project, click **+ New** → **Database** → **Add PostgreSQL**.
2. Railway provisions a managed PostgreSQL 15 instance and injects `DATABASE_URL` automatically.
3. Note the internal hostname: `postgres.railway.internal`.

### Redis

1. Click **+ New** → **Database** → **Add Redis**.
2. Railway provisions Redis 7 and injects `REDIS_URL` automatically.
3. Internal hostname: `redis.railway.internal`.

### InfluxDB

Railway does not have a native InfluxDB plugin. Deploy it as a Docker service:

1. Click **+ New** → **Docker Image**.
2. Image: `influxdb:2.7-alpine`
3. Set the following environment variables on this service:
   ```
   DOCKER_INFLUXDB_INIT_MODE=setup
   DOCKER_INFLUXDB_INIT_USERNAME=admin
   DOCKER_INFLUXDB_INIT_PASSWORD=<strong-password>
   DOCKER_INFLUXDB_INIT_ORG=cardioguard
   DOCKER_INFLUXDB_INIT_BUCKET=wellness_metrics
   DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=<your-influxdb-token>
   ```
4. Add a volume mount: `/var/lib/influxdb2` → persistent volume.
5. Internal hostname: `influxdb.railway.internal`.

---

## Step 3 — Deploy the API Gateway

1. In your Railway project, click **+ New** → **GitHub Repo** → select `CardioGuardAI`.
2. Set the **Root Directory** to `backend/api-gateway`.
3. Railway will detect the `Dockerfile` and use it automatically.
4. Set the **Start Command** (if not using Dockerfile): `node server.js`
5. Set **Port**: `3000`
6. Rename the service to `api-gateway`.

---

## Step 4 — Deploy the Wellness Engine

1. Click **+ New** → **GitHub Repo** → select `CardioGuardAI` again.
2. Set the **Root Directory** to `backend/app`.
3. Railway will detect the `Dockerfile` and use it automatically.
4. Set **Port**: `8000`
5. Rename the service to `wellness-engine`.
6. **Do not expose this service publicly** — it should only be reachable from `api-gateway` over the private network.

---

## Step 5 — Configure Environment Variables

### api-gateway service

Navigate to `api-gateway` → **Variables** and add:

```
PORT=3000
NODE_ENV=production
JWT_SECRET=<generate with: openssl rand -hex 64>
PYTHON_BACKEND_URL=http://wellness-engine.railway.internal:8000
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

> Railway supports variable references with `${{ServiceName.VARIABLE}}` syntax. Use `${{Postgres.DATABASE_URL}}` to automatically inject the PostgreSQL connection string.

### wellness-engine service

Navigate to `wellness-engine` → **Variables** and add:

```
PYTHON_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_HOST=redis.railway.internal
REDIS_PORT=6379
INFLUXDB_URL=http://influxdb.railway.internal:8086
INFLUXDB_ORG=cardioguard
INFLUXDB_BUCKET=wellness_metrics
INFLUXDB_TOKEN=<your-influxdb-token>
```

### Optional integrations

Add to whichever service needs them:

```
WHATSAPP_API_KEY=<Meta Cloud API key>
ANTHROPIC_API_KEY=<Claude API key>
```

---

## Step 6 — Service Networking

Railway services within the same project communicate over a private network using the pattern:

```
http://<service-name>.railway.internal:<port>
```

| From | To | URL |
|---|---|---|
| `api-gateway` | `wellness-engine` | `http://wellness-engine.railway.internal:8000` |
| `wellness-engine` | `postgres` | Injected via `DATABASE_URL` |
| `wellness-engine` | `redis` | `redis://redis.railway.internal:6379` |
| `wellness-engine` | `influxdb` | `http://influxdb.railway.internal:8086` |

**Important:** Only expose `api-gateway` to the public internet. Keep `wellness-engine`, `postgres`, `redis`, and `influxdb` on the private network only.

To expose `api-gateway`:
1. Go to `api-gateway` → **Settings** → **Networking**.
2. Click **Generate Domain** to get a `*.up.railway.app` URL, or add your custom domain.

---

## Step 7 — Database Initialisation

Railway's PostgreSQL plugin does not run init scripts automatically. Run the schema migrations once after the first deploy:

### Using Railway CLI

```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations via the api-gateway service
railway run --service api-gateway \
  psql "$DATABASE_URL" -f backend/api-gateway/setup_db.sql

railway run --service api-gateway \
  psql "$DATABASE_URL" -f backend/api-gateway/init_db.sql
```

### Using Railway's built-in shell

1. Go to `postgres` service → **Connect** → **Query**.
2. Paste the contents of `backend/api-gateway/setup_db.sql` and execute.
3. Repeat for `backend/api-gateway/init_db.sql`.

---

## Step 8 — Health Checks & Monitoring

### Configure health checks in Railway

For each application service, go to **Settings** → **Health Check**:

**api-gateway:**
- Path: `/health`
- Port: `3000`
- Timeout: `10s`

**wellness-engine:**
- Path: `/health`
- Port: `8000`
- Timeout: `10s`

### Expected health responses

```json
// GET http://<api-gateway-domain>/health
{
  "status": "healthy",
  "service": "api-gateway",
  "uptime": 3600.5,
  "timestamp": "2024-01-15T10:30:00.000Z"
}

// GET http://wellness-engine.railway.internal:8000/health
{
  "status": "healthy"
}
```

### Monitoring

Railway provides built-in metrics (CPU, memory, network) in the **Metrics** tab of each service. For application-level observability:

- **Logs:** Railway streams stdout/stderr in real time. Use `railway logs --service api-gateway` from the CLI.
- **Alerts:** Configure Railway notification webhooks under **Project Settings** → **Webhooks** to receive deploy and crash alerts.
- **Uptime monitoring:** Use an external service (e.g. Better Uptime, UptimeRobot) to monitor `GET /health` on your public domain.

---

## Step 9 — Custom Domains

1. Go to `api-gateway` → **Settings** → **Networking** → **Custom Domain**.
2. Add your domain (e.g. `api.cardioguardai.in`).
3. Railway provides the CNAME target — add it to your DNS provider.
4. SSL is provisioned automatically via Let's Encrypt.

For the patient PWA (`cardioguardai.in`), deploy `frontend-patient/dist/` as a static site (Railway static service or Vercel/Netlify) and point it at your `api-gateway` domain.

---

## Troubleshooting

### Service fails to start

- Check **Logs** in the Railway dashboard for the failing service.
- Verify all required environment variables are set (especially `JWT_SECRET`, `DATABASE_URL`).
- Ensure the `Dockerfile` is present in the correct root directory.

### api-gateway cannot reach wellness-engine

- Confirm `PYTHON_BACKEND_URL` is set to `http://wellness-engine.railway.internal:8000`.
- Verify both services are in the **same Railway project** (private networking is project-scoped).
- Check that `wellness-engine` is running and its health check passes.

### Database connection errors

- Confirm `DATABASE_URL` uses the Railway-injected value (`${{Postgres.DATABASE_URL}}`).
- Check that the PostgreSQL service is healthy in the Railway dashboard.
- Verify the schema has been initialised (Step 7).

### InfluxDB token errors

- Ensure `INFLUXDB_TOKEN` matches `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` set on the InfluxDB service.
- If you regenerated the token in the InfluxDB UI, update `INFLUXDB_TOKEN` on `wellness-engine`.

### Cold start latency

Railway services may have cold starts on the free/hobby tier. To minimise:
- Enable **Always On** in service settings (requires paid plan).
- Configure health check retries to allow for startup time (`start_period: 30s`).

### Deploy stuck in "Building"

- Check that the `Dockerfile` `COPY` paths are correct relative to the root directory.
- Ensure `requirements.txt` (Python) or `package.json` (Node) are present in the root directory of each service.

---

> For additional help, see the [Railway documentation](https://docs.railway.app) or open an issue in the CardioGuard AI repository.
