# CardioGuard AI — API Reference

> **Base URL (local):** `http://localhost:3000`
> **Base URL (production):** `https://api.cardioguardai.in`
>
> **Disclaimer:** All endpoints return a `disclaimer` field confirming this is a general wellness platform, not a medical device.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Wellness Metrics](#wellness-metrics)
3. [Wellness Assessment (Brain)](#wellness-assessment-brain)
4. [System](#system)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Request / Response Examples](#request--response-examples)

---

## Authentication

All protected endpoints require a **Bearer JWT token** in the `Authorization` header:

```
Authorization: Bearer <token>
```

Tokens are issued on login/register and expire after **7 days**.

---

### POST /api/v1/auth/register

Register a new user account.

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Arjun Sharma",
  "phone": "+919876543210"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | Minimum 8 characters |
| `full_name` | string | Yes | User's display name |
| `phone` | string | No | E.164 format phone number |

**Response `201 Created`:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "Arjun Sharma",
    "preferred_language": "en"
  },
  "disclaimer": "General Wellness Platform: Acknowledgment recorded."
}
```

**Error responses:**

| Status | Condition |
|---|---|
| `400` | User with this email already exists |
| `500` | Server error |

---

### POST /api/v1/auth/login

Authenticate an existing user and receive a JWT.

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response `200 OK`:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "Arjun Sharma"
  },
  "disclaimer": "General Wellness Platform: Metrics tracked are for lifestyle coaching only."
}
```

**Error responses:**

| Status | Condition |
|---|---|
| `400` | Invalid credentials (user not found or wrong password) |
| `500` | Server error |

---

## Wellness Metrics

These endpoints store and retrieve raw biometric readings in PostgreSQL. They are handled entirely by the API Gateway.

---

### POST /api/v1/metrics/ingest

Submit a single wellness metric reading. **Requires JWT.**

**Request body:**

```json
{
  "metric_type": "heart_rate",
  "value": 72,
  "source": "manual",
  "quality_score": 0.95,
  "metadata": {
    "device": "Apple Watch Series 9",
    "activity": "resting"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `metric_type` | string | Yes | One of: `heart_rate`, `blood_pressure`, `spo2`, `bmi`, `steps`, `sleep_hours` |
| `value` | number | Yes | Numeric reading |
| `source` | string | Yes | One of: `manual`, `ppg_wearable`, `rppg_camera`, `user_input` |
| `quality_score` | number | No | Signal quality 0.00–1.00 |
| `metadata` | object | No | Arbitrary key-value context |

**Response `201 Created`:**

```json
{
  "message": "Metric recorded successfully",
  "metric": {
    "metric_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "metric_type": "heart_rate",
    "source": "manual",
    "quality_score": 0.95,
    "metadata": { "device": "Apple Watch Series 9", "activity": "resting" },
    "measurement_timestamp": "2024-01-15T10:30:00.000Z",
    "created_at": "2024-01-15T10:30:00.123Z"
  },
  "disclaimer": "General Wellness Tracking: Not for medical diagnosis."
}
```

---

### GET /api/v1/metrics/history

Retrieve a user's metric history for a given type. **Requires JWT.**

**Query parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `type` | string | Yes | — | Metric type (e.g. `heart_rate`) |
| `limit` | integer | No | `50` | Maximum records to return (max 200) |

**Example request:**

```
GET /api/v1/metrics/history?type=heart_rate&limit=10
Authorization: Bearer <token>
```

**Response `200 OK`:**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "metric_type": "heart_rate",
  "history": [
    {
      "metric_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "metric_type": "heart_rate",
      "source": "manual",
      "quality_score": 0.95,
      "metadata": {},
      "measurement_timestamp": "2024-01-15T10:30:00.000Z"
    }
  ],
  "disclaimer": "Educational history for personal wellness tracking."
}
```

---

## Wellness Assessment (Brain)

These endpoints are proxied by the API Gateway to the Python Wellness Engine. The JWT is verified at the gateway; the user's ID is forwarded via the `x-user-id` header.

All `/api/v1/brain/*` paths map to `/api/v1/*` on the Wellness Engine.

---

### POST /api/v1/brain/vitals/ingest

Submit a full biometric feature vector for multi-agent wellness analysis. Returns a **Wellness Assessment Index** (0–100) and pattern observations. **Requires JWT.**

**Request body:**

```json
{
  "age": 45,
  "sex": "M",
  "bmi": 27.3,
  "current_vitals": {
    "hr": 88,
    "sbp": 138,
    "dbp": 88
  },
  "symptoms": ["shortness_of_breath"],
  "history_flags": {
    "diabetes": false,
    "hypertension": true,
    "user_display_name": "Arjun Sharma",
    "location": "New Delhi"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `age` | integer | Yes | Age in years |
| `sex` | string | Yes | `"M"`, `"F"`, or `"O"` |
| `bmi` | float | Yes | Body Mass Index |
| `current_vitals` | object | Yes | Map of vital readings |
| `current_vitals.hr` | float | Yes | Heart rate (bpm) |
| `current_vitals.sbp` | float | No | Systolic blood pressure (mmHg) |
| `current_vitals.dbp` | float | No | Diastolic blood pressure (mmHg) |
| `symptoms` | array | No | Reported symptoms: `chest_pain`, `shortness_of_breath`, `dizziness`, `fatigue` |
| `history_flags` | object | No | Lifestyle/history context flags |

**Response `200 OK`:**

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "neural_assessment_vector": 62,
  "significant_observations": [
    {
      "pattern_name": "Cardiovascular Wellness Pattern (Neural Assessment)",
      "assessment_index": 0.62,
      "confidence_interval": [0.57, 0.67],
      "observation_level": "significant_deviation",
      "contributing_factors": ["elevated_heart_rate", "hypertension"]
    }
  ],
  "wellness_suggestion": "Wellness Companion: Noticeable pattern deviation. Consider scheduling a routine wellness consultation with a healthcare provider.",
  "significant_deviation_detected": false,
  "nearest_healthcare_resource": null
}
```

**Observation levels:**

| Level | `assessment_index` Range | Meaning |
|---|---|---|
| `baseline` | 0.00 – 0.20 | Within personal wellness baseline |
| `moderate_deviation` | 0.20 – 0.50 | Minor change from usual patterns |
| `significant_deviation` | 0.50 – 0.80 | Noticeable deviation — consider consulting a provider |
| `urgent_evaluation` | 0.80 – 1.00 | Significant deviation — strongly recommend professional evaluation |

**When `significant_deviation_detected` is `true`:**

The response includes `nearest_healthcare_resource` and triggers a WhatsApp broadcast to the ASHA coordinator (if configured). The `wellness_suggestion` will recommend immediate professional evaluation.

```json
{
  "significant_deviation_detected": true,
  "nearest_healthcare_resource": {
    "name": "AIIMS Delhi",
    "distance_km": 5.2,
    "type": "Tertiary Care Hospital",
    "contact": "+91-11-2658-8500"
  },
  "wellness_suggestion": "Significant deviation from personal wellness baseline. We recommend consulting a healthcare professional for a formal medical evaluation. (Coordination Agent: High Priority detected. Navigator Agent identified nearest facility.)"
}
```

---

### GET /api/v1/brain/vitals/history

Retrieve the wellness assessment history for the authenticated user. **Requires JWT.**

**Query parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `patient_id` | string | No | `patient_001` | Patient identifier (future multi-patient support) |

**Response `200 OK`:**

```json
[
  {
    "patient_id": "patient_001",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "neural_assessment_vector": 62,
    "significant_deviation_detected": false,
    "wellness_suggestion": "Wellness Companion: Monitor regularly and maintain healthy lifestyle"
  }
]
```

---

## System

### GET /health

API Gateway health check. No authentication required.

**Response `200 OK`:**

```json
{
  "status": "healthy",
  "service": "api-gateway",
  "uptime": 3600.5,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### GET / (root)

Returns service information and available endpoint groups.

**Response `200 OK`:**

```json
{
  "message": "CardioGuard AI API Gateway is operational",
  "version": "1.0.0",
  "disclaimer": "General Wellness & Lifestyle Monitoring Platform - Non-Medical Service",
  "endpoints": {
    "auth": "/api/v1/auth",
    "metrics": "/api/v1/metrics",
    "brain": "/api/v1/brain (protected)"
  }
}
```

---

## Error Handling

All errors follow a consistent JSON structure:

```json
{
  "message": "Human-readable error description",
  "error": "Technical error detail (development only)"
}
```

**Standard HTTP status codes:**

| Code | Meaning |
|---|---|
| `200` | Success |
| `201` | Resource created |
| `400` | Bad request — invalid input or missing required fields |
| `401` | Unauthorised — missing or invalid JWT |
| `404` | Resource not found |
| `429` | Too many requests — rate limit exceeded |
| `500` | Internal server error |
| `502` | Bad gateway — Wellness Engine is unreachable |

**502 Bad Gateway example** (Wellness Engine down):

```json
{
  "error": "Wellness Engine (Python) is currently unavailable",
  "message": "We are working to restore the connection to our analysis agents.",
  "disclaimer": "In case of urgent wellness concerns, please consult a healthcare provider directly."
}
```

---

## Rate Limiting

The API Gateway does not currently enforce rate limiting at the middleware level (planned). The legacy Flask app (`app.py`) enforces:

| Endpoint | Limit |
|---|---|
| `POST /api/predict` | 10 requests / minute |
| `POST /api/chat` | 5 requests / minute |
| All others | 200 / day, 50 / hour |

For production deployments on Railway, configure rate limiting at the Railway edge or add `express-rate-limit` middleware to `backend/api-gateway/server.js`.

---

## Request / Response Examples

### Full wellness assessment flow (cURL)

```bash
# Step 1: Register
curl -s -X POST https://api.cardioguardai.in/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "arjun@example.com",
    "password": "Wellness2024!",
    "full_name": "Arjun Sharma",
    "phone": "+919876543210"
  }' | jq .

# Step 2: Login
TOKEN=$(curl -s -X POST https://api.cardioguardai.in/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"arjun@example.com","password":"Wellness2024!"}' \
  | jq -r '.token')

# Step 3: Record a heart rate metric
curl -s -X POST https://api.cardioguardai.in/api/v1/metrics/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_type": "heart_rate",
    "value": 88,
    "source": "ppg_wearable",
    "quality_score": 0.92
  }' | jq .

# Step 4: Run a full wellness assessment
curl -s -X POST https://api.cardioguardai.in/api/v1/brain/vitals/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "sex": "M",
    "bmi": 27.3,
    "current_vitals": {"hr": 88, "sbp": 138, "dbp": 88},
    "symptoms": ["shortness_of_breath"],
    "history_flags": {
      "hypertension": true,
      "user_display_name": "Arjun Sharma",
      "location": "New Delhi"
    }
  }' | jq .

# Step 5: Retrieve metric history
curl -s "https://api.cardioguardai.in/api/v1/metrics/history?type=heart_rate&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Python client example

```python
import httpx

BASE_URL = "https://api.cardioguardai.in"

# Login
resp = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "arjun@example.com",
    "password": "Wellness2024!"
})
token = resp.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# Submit wellness assessment
assessment = httpx.post(
    f"{BASE_URL}/api/v1/brain/vitals/ingest",
    headers=headers,
    json={
        "age": 45,
        "sex": "M",
        "bmi": 27.3,
        "current_vitals": {"hr": 88, "sbp": 138, "dbp": 88},
        "symptoms": ["shortness_of_breath"],
        "history_flags": {"user_display_name": "Arjun Sharma"}
    }
).json()

print(f"Wellness Index: {assessment['neural_assessment_vector']}/100")
print(f"Suggestion: {assessment['wellness_suggestion']}")
```

---

> For interactive API exploration, visit `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc) when running locally.
