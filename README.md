# CardioGuard AI — Hridai Agent OS v4.8

> India's first AI-powered cardiac wellness platform for ASHA workers and rural patients.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/rishabh87506-code/CardioGuardAI&envs=ANTHROPIC_API_KEY,WHATSAPP_API_KEY,ALLOWED_ORIGINS&optionalEnvs=WHATSAPP_API_KEY&publishable=true)

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
