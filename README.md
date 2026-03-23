# CardioGuard AI — Hridai Agent OS

> India's first AI-powered general wellness platform for ASHA workers and rural patients.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/rishabh87506-code/CardioGuardAI&envs=JWT_SECRET,PYTHON_BACKEND_URL,DATABASE_URL&publishable=true)

> **Disclaimer:** CardioGuard AI is a **general wellness and lifestyle monitoring platform**. It is NOT a medical device, does NOT diagnose disease, and does NOT replace professional medical advice. Always consult a qualified healthcare provider for clinical decisions. Compliant with India's DPDP Act 2023. Exempt from FDA/CDSCO medical device regulations.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Local Development (Docker Compose)](#local-development-docker-compose)
5. [Manual Setup (Without Docker)](#manual-setup-without-docker)
6. [Environment Variables](#environment-variables)
7. [Database Setup](#database-setup)
8. [API Documentation](#api-documentation)
9. [Testing](#testing)
10. [Deployment to Railway](#deployment-to-railway)
11. [Wellness Compliance Notes](#wellness-compliance-notes)
12. [Contributing](#contributing)

---

## Project Overview

CardioGuard AI is a microservices-based wellness platform that:

- Collects biometric data (heart rate, blood pressure, BMI, symptoms) from users via a Progressive Web App
- Runs a multi-agent ML pipeline (Random Forest, 8-feature model) to compute a **Wellness Assessment Index** (0–100)
- Stores structured data in **PostgreSQL**, time-series metrics in **InfluxDB**, and caches sessions in **Redis**
- Dispatches wellness broadcasts via WhatsApp and notifies ASHA community health workers for high-deviation events
- Serves a patient-facing PWA and a static portal

**India-first design:** Bilingual (Hindi + English), ASHA worker integration, offline-first PWA, low-bandwidth optimised.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│   Patient PWA (frontend-patient/)   Static Portal (/portal)    │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────────┐
│              API Gateway  (Node.js / Express)                   │
│              backend/api-gateway/  — port 3000                  │
│                                                                 │
│  POST /api/v1/auth/register   POST /api/v1/auth/login           │
│  POST /api/v1/metrics/ingest  GET  /api/v1/metrics/history      │
│  /api/v1/brain/*  ──── JWT-protected reverse proxy ────────►   │
└────────────────────────┬────────────────────────────────────────┘
                         │ Internal HTTP (x-user-id header)
┌────────────────────────▼────────────────────────────────────────┐
│           Wellness Engine  (Python / FastAPI)                   │
│           backend/app/  — port 8000                             │
│                                                                 │
│  POST /api/v1/vitals/ingest   GET /api/v1/vitals/history        │
│  Multi-agent pipeline: Risk Engine → Coordinator → Companion    │
└──────┬──────────────────┬──────────────────────┬───────────────┘
       │                  │                      │
┌──────▼──────┐  ┌────────▼────────┐  ┌──────────▼──────────┐
│ PostgreSQL  │  │    InfluxDB     │  │       Redis          │
│ (users,     │  │ (time-series    │  │  (session cache,     │
│  metrics,   │  │  vitals)        │  │   rate limiting)     │
│  contacts)  │  └─────────────────┘  └─────────────────────┘
└─────────────┘
```

**Service responsibilities:**

| Service | Language | Port | Responsibility |
|---|---|---|---|
| `api-gateway` | Node.js 18 / Express | 3000 | Auth, JWT, metrics CRUD, reverse proxy |
| `wellness-engine` | Python 3.11 / FastAPI | 8000 | ML inference, multi-agent orchestration |
| `postgres` | PostgreSQL 15 | 5432 | Users, wellness metrics, contacts |
| `influxdb` | InfluxDB 2.7 | 8086 | Time-series biometric data |
| `redis` | Redis 7 | 6379 | Session cache, rate limiting |

---

## Prerequisites

| Tool | Minimum Version | Install |
|---|---|---|
| Docker | 24.x | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.x (bundled with Docker Desktop) | — |
| Node.js | 18.x | [nodejs.org](https://nodejs.org/) (for local dev without Docker) |
| Python | 3.11.x | [python.org](https://www.python.org/) (for local dev without Docker) |
| Git | any | — |

---

## Local Development (Docker Compose)

This is the recommended way to run the full stack locally.

### 1. Clone the repository

```bash
git clone https://github.com/rishabh87506-code/CardioGuardAI.git
cd CardioGuardAI
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum change JWT_SECRET and PG_PASSWORD
```

### 3. Start all services

```bash
docker compose up --build
```

Services will start in dependency order. On first run, PostgreSQL will automatically execute the schema migrations in `backend/api-gateway/setup_db.sql` and `init_db.sql`.

### 4. Verify everything is running

```bash
# API Gateway health
curl http://localhost:3000/health

# Wellness Engine health
curl http://localhost:8000/health

# Interactive API docs (FastAPI Swagger UI)
open http://localhost:8000/docs
```

### 5. Stop the stack

```bash
docker compose down          # stop containers, keep volumes
docker compose down -v       # stop containers AND delete volumes (fresh start)
```

---

## Manual Setup (Without Docker)

### API Gateway (Node.js)

```bash
cd backend/api-gateway
npm install
cp ../../.env.example .env   # edit as needed
node server.js               # or: npm run dev (hot-reload with nodemon)
```

### Wellness Engine (Python)

```bash
cd backend/app
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example .env   # edit as needed
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure the following:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `3000` | API Gateway listen port |
| `NODE_ENV` | `development` | Node environment |
| `JWT_SECRET` | *(required)* | JWT signing secret — use `openssl rand -hex 64` |
| `PYTHON_BACKEND_URL` | `http://wellness-engine:8000` | Internal URL of Wellness Engine |
| `DATABASE_URL` | *(required)* | Full PostgreSQL connection string |
| `PG_HOST` | `postgres` | PostgreSQL host |
| `PG_PORT` | `5432` | PostgreSQL port |
| `PG_DATABASE` | `cardioguard` | Database name |
| `PG_USER` | `cardioguard_user` | Database user |
| `PG_PASSWORD` | *(required)* | Database password |
| `REDIS_HOST` | `redis` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `INFLUXDB_URL` | `http://influxdb:8086` | InfluxDB URL |
| `INFLUXDB_ORG` | `cardioguard` | InfluxDB organisation |
| `INFLUXDB_BUCKET` | `wellness_metrics` | InfluxDB bucket |
| `INFLUXDB_TOKEN` | *(required)* | InfluxDB API token |
| `WHATSAPP_API_KEY` | *(optional)* | Meta Cloud API key for broadcasts |
| `ANTHROPIC_API_KEY` | *(optional)* | Claude API key for AI guidance |

---

## Database Setup

The PostgreSQL schema is applied automatically when using Docker Compose (via `docker-entrypoint-initdb.d`).

For manual setup:

```bash
psql -U postgres -c "CREATE DATABASE cardioguard;"
psql -U postgres -d cardioguard -f backend/api-gateway/setup_db.sql
psql -U postgres -d cardioguard -f backend/api-gateway/init_db.sql
```

**Key tables:**

| Table | Purpose |
|---|---|
| `users` | User accounts with consent flags |
| `wellness_metrics` | Biometric readings with quality scores |
| `family_contacts` | Emergency/family notification contacts |
| `asha_workers` | Community health worker registry |
| `healthcare_facilities` | Nearby facility directory |

---

## API Documentation

Full interactive documentation is available at `http://localhost:8000/docs` (Swagger UI) when the Wellness Engine is running.

See [`docs/API.md`](docs/API.md) for the complete reference including authentication, request/response examples, and error codes.

**Quick reference:**

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | None | API Gateway health check |
| `POST` | `/api/v1/auth/register` | None | Register new user |
| `POST` | `/api/v1/auth/login` | None | Login, receive JWT |
| `POST` | `/api/v1/metrics/ingest` | JWT | Submit a wellness metric |
| `GET` | `/api/v1/metrics/history` | JWT | Retrieve metric history |
| `POST` | `/api/v1/brain/vitals/ingest` | JWT | Full wellness assessment |
| `GET` | `/api/v1/brain/vitals/history` | JWT | Assessment history |

---

## Testing

### API Gateway (Node.js)

```bash
cd backend/api-gateway
npm test
```

### Wellness Engine (Python)

```bash
cd backend
python -m pytest tests/ -v
```

### Manual smoke test

```bash
# 1. Register
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!","full_name":"Test User","phone":"+919876543210"}'

# 2. Login and capture token
TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")

# 3. Submit a wellness metric
curl -X POST http://localhost:3000/api/v1/metrics/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"metric_type":"heart_rate","value":72,"source":"manual","quality_score":0.95}'

# 4. Run a full wellness assessment
curl -X POST http://localhost:3000/api/v1/brain/vitals/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35, "sex": "M", "bmi": 24.5,
    "current_vitals": {"hr": 72, "sbp": 118, "dbp": 76},
    "symptoms": [],
    "history_flags": {"user_display_name": "Test User"}
  }'
```

---

## Deployment to Railway

See the full step-by-step guide in [`docs/RAILWAY_DEPLOYMENT.md`](docs/RAILWAY_DEPLOYMENT.md).

**Quick summary:**

1. Push this repository to GitHub
2. Create a new Railway project and connect the repo
3. Add **PostgreSQL**, **Redis**, and **InfluxDB** plugins from the Railway marketplace
4. Create two services: `api-gateway` (root: `backend/api-gateway`) and `wellness-engine` (root: `backend/app`)
5. Set environment variables from `.env.example` in each service's settings
6. Railway auto-deploys on every push to `main`

---

## Wellness Compliance Notes

CardioGuard AI is designed and operated as a **general wellness platform** under the following framework:

- **Not a Medical Device:** No diagnosis, treatment, cure, or prevention of disease. Exempt from FDA 21 CFR Part 880 and CDSCO medical device regulations.
- **DPDP Act 2023 Compliant:** Explicit user consent collected at registration (`consent_wellness_tracking`, `consent_family_sharing`, `consent_asha_contact` flags in the `users` table). Data minimisation and purpose limitation enforced.
- **Language:** All user-facing copy uses wellness language ("deviation from baseline", "wellness index") rather than clinical language ("diagnosis", "disease", "treatment").
- **Disclaimers:** Every API response includes a `disclaimer` field reinforcing the non-medical nature of the platform.
- **Data Residency:** Designed for India-first deployment. Use Railway's Mumbai region or equivalent for data residency compliance.

---

## Contributing

1. Fork the repository and create a feature branch: `git checkout -b feat/your-feature`
2. Follow the existing code style (ESLint for JS, Black/isort for Python)
3. Add tests for new functionality
4. Ensure all health checks pass: `docker compose up --build`
5. Open a pull request with a clear description of the change

**Commit convention:** `type(scope): description` — e.g. `feat(api-gateway): add rate limiting middleware`

---

© 2026 CardioGuard AI — [cardioguardai.in](https://cardioguardai.in) | [cardioguardai.co.in](https://cardioguardai.co.in)

---

## Domains

| Domain | Purpose |
|---|---|
| **cardioguardai.in** | Patient assessment application |
| **cardioguardai.co.in** | Investor & marketing landing page |
| **/pitch** | Investor pitch (alias, always accessible) |

---

## Agent Network (v4.8)

- **Antigravity-22 Engine** — GradientBoosting classifier, 22 cardiac features, AUC 0.81, SHAP explainability
- **Hridai Brain** — Claude Sonnet bilingual (Hindi + English) wellness guidance
- **ASHA Dispatch Agent** — Auto WhatsApp alert at ≥70% risk score
- **Batch API** — Health camp priority queue (up to 100 patients)

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | App (cardioguardai.in) or Pitch (cardioguardai.co.in) |
| GET | `/pitch` | Investor landing page (always) |
| GET | `/health` or `/api/health` | System health check |
| POST | `/api/predict` | Risk assessment (10/min rate limit) |
| POST | `/api/batch` | Batch assessment for ASHA workers |
| POST | `/api/chat` | Claude Sonnet proxy (5/min rate limit) |

## Quick Start (Local)

```bash
git clone <repo>
cd "CardioGuard AI"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python3 app.py
# App:   http://localhost:5005
# Pitch: http://localhost:5005/pitch
```

## Train the Model

```bash
python3 scripts/train_model.py
# Trains on 10,000 synthetic patients
# Reports 5-fold CV AUC + holdout metrics
# Saves to model/antigravity_model.pkl
```

## Environment Variables (Railway)

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key for AI guidance |
| `WHATSAPP_API_KEY` | No | Meta Cloud API (mock mode if empty) |
| `ALLOWED_ORIGINS` | No | CORS origins (defaults to both domains) |

## Risk Thresholds (v4.8 Wellness Compliance)

| Score | Category | Action |
|---|---|---|
| 0–29% | OPTIMAL | Monitor, healthy lifestyle |
| 30–69% | MODERATE DEVIATION | Doctor consultation recommended |
| ≥70% | CRITICAL DEVIATION | ASHA WhatsApp alert auto-dispatched |

## Project Structure

```
CardioGuard AI/
├── app.py                  # Production Flask entry point
├── landing.html            # Investor pitch (cardioguardai.co.in)
├── index.html              # Patient assessment app (cardioguardai.in)
├── requirements.txt        # Python dependencies
├── Procfile                # Railway: gunicorn app:app
├── model/
│   └── antigravity_model.pkl
├── scripts/
│   ├── train_model.py      # Model training pipeline
│   └── generate_docs.py    # PDF documentation generator
└── docs/
    └── CardioGuardAI_Technical_Documentation.pdf
```

---

> **Disclaimer:** CardioGuard AI is a non-diagnostic wellness support tool. Not a medical device. Always consult a qualified physician for clinical decisions.

© 2026 CardioGuard AI — cardioguardai.in | cardioguardai.co.in
