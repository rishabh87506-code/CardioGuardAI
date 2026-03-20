"""
CardioGuard AI — Merged Production Backend (v4.5)
================================================
Combines Antigravity Risk Engine + Secure Hridai Proxy
Designed for Railway/Cloud Run deployment.
"""

import os
import json
import time
import pickle
import joblib
import numpy as np
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# In production, specify your frontend domain in ALLOWED_ORIGINS
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
CORS(app, origins=ALLOWED_ORIGINS)

# ── CONFIGURATION ──────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'antigravity_model.pkl')

# ── LOAD RISK MODEL ────────────────────────────────────
def load_risk_model():
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Model not found at {MODEL_PATH}. Prediction service will be offline.")
        return None
    try:
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    except:
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return None

model = load_risk_model()

# ── SHAP EXPLAINER ─────────────────────────────────────
explainer = None
if model:
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        print("✓ SHAP explainer ready")
    except Exception as e:
        print(f"ℹ SHAP not initialized: {e}")

# ── FEATURE SPEC ───────────────────────────────────────
FEATURES = [
    "age","sex","cholesterol","blood_pressure","heart_rate",
    "diabetes","family_history","smoking","obesity","alcohol_consumption",
    "exercise_hours_per_week","diet","previous_heart_problems","medication_use",
    "stress_level","sedentary_hours_per_day","bmi","triglycerides",
    "physical_activity_days_per_week","sleep_hours_per_day","chest_pain","blood_sugar"
]

DISPLAY_NAMES = {
    "age": "Umar (Age)", "sex": "Gender", "cholesterol": "Cholesterol",
    "blood_pressure": "Blood Pressure", "heart_rate": "Heart Rate",
    "diabetes": "Diabetes", "family_history": "Family History",
    "smoking": "Smoking", "obesity": "Obesity", "triglycerides": "Triglycerides",
    "bmi": "BMI", "blood_sugar": "Blood Sugar", "chest_pain": "Chest Pain"
}

# ── ROUTE: HEALTH ──────────────────────────────────────
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "live",
        "service": "CardioGuardAI Merged Engine",
        "version": "4.5",
        "model_loaded": model is not None,
        "claude_configured": len(ANTHROPIC_API_KEY) > 20,
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
        "timestamp": time.time()
    })

# ── ROUTE: RISK PREDICTION ─────────────────────────────
@app.route('/api/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Risk model not loaded on server."}), 503
    
    try:
        data = request.get_json(force=True)
        # Validate all 22 features
        fa_list = []
        for f in FEATURES:
            if f not in data:
                return jsonify({"error": f"Missing feature: {f}"}), 400
            fa_list.append(float(data[f]))

        fa = np.array(fa_list).reshape(1, -1)
        prob = float(model.predict_proba(fa)[0][1])
        
        # Risk levels
        level = "LOW"
        if prob >= 0.60: level = "HIGH"
        elif prob >= 0.30: level = "MODERATE"

        # SHAP Explanations
        shap_vals = {}
        if explainer:
            try:
                sv = explainer.shap_values(fa)
                vals = sv[1][0] if isinstance(sv, list) else sv[0]
                for nm, v in zip(FEATURES, vals):
                    display_nm = DISPLAY_NAMES.get(nm, nm.replace('_', ' ').title())
                    shap_vals[display_nm] = {
                        "impact": round(abs(float(v)) * 100, 2),
                        "direction": "increases" if v > 0 else "decreases"
                    }
                # Sort by impact
                shap_vals = dict(sorted(shap_vals.items(), key=lambda x: x[1]['impact'], reverse=True))
            except: pass

        return jsonify({
            "risk_score": round(prob * 100, 2),
            "risk_level": level,
            "shap_values": shap_vals,
            "proxy_mode": True,
            "disclaimer": "Non-diagnostic wellness assessment."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── ROUTE: CLAUDE PROXY ────────────────────────────────
@app.route('/api/chat', methods=['POST'])
def chat():
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "Anthropic API Key not configured on proxy server."}), 503
    
    try:
        data = request.get_json(force=True)
        # Forward to Anthropic
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": data.get("model", "claude-3-sonnet-20240229"),
                "max_tokens": data.get("max_tokens", 1024),
                "system": data.get("system", ""),
                "messages": data.get("messages", [])
            },
            timeout=30
        )
        return (res.text, res.status_code, res.headers.items())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port)
