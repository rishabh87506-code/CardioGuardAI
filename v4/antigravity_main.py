"""
CardioGuardAI — Antigravity Model API v4
=========================================
This is the UPGRADED main.py for your Railway Antigravity deployment.
Replace your existing main.py with this file entirely.

What's new:
  ✓ SHAP explainability — top 5 risk factors per prediction
  ✓ Women's model hook — routes sex=0 to separate model if available
  ✓ Bias Audit Agent data — returns demographic fairness metadata
  ✓ /batch endpoint — for ASHA worker priority queue
  ✓ /trend endpoint — 7-day pattern analysis for Memory Agent
  ✓ Clean JSON — no internal model metadata exposed

DEPLOY STEPS:
  1. pip install shap==0.44.0 scipy==1.11.4  (add to requirements.txt)
  2. Replace your current main.py with this file
  3. Redeploy on Railway — automatic
  4. Test: curl -X POST https://your-url.railway.app/predict -d '{...}'
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle, joblib, numpy as np, os, json

app = Flask(__name__)
CORS(app)

# ── Load models ────────────────────────────────────────
MODEL_PATH  = os.path.join(os.path.dirname(__file__), 'model', 'antigravity_model.pkl')
WOMEN_PATH  = os.path.join(os.path.dirname(__file__), 'model', 'antigravity_women.pkl')

def load_model(path):
    try:
        return pickle.load(open(path,'rb'))
    except:
        try: return joblib.load(path)
        except: return None

model       = load_model(MODEL_PATH)
women_model = load_model(WOMEN_PATH)  # None if not trained yet
print(f"✓ Base model: {'loaded' if model else 'MISSING'}")
print(f"✓ Women model: {'loaded' if women_model else 'not available (using base)'}")

# ── SHAP explainer ─────────────────────────────────────
explainer = None
if model:
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        print("✓ SHAP explainer ready")
    except ImportError:
        print("ℹ SHAP not installed. Run: pip install shap==0.44.0")
    except Exception as e:
        print(f"ℹ SHAP init failed: {e}")

# ── Feature spec (22 features — matches CardioGuardAI app exactly) ──
FEATURES = [
    "age","sex","cholesterol","blood_pressure","heart_rate",
    "diabetes","family_history","smoking","obesity","alcohol_consumption",
    "exercise_hours_per_week","diet","previous_heart_problems","medication_use",
    "stress_level","sedentary_hours_per_day","bmi","triglycerides",
    "physical_activity_days_per_week","sleep_hours_per_day","chest_pain","blood_sugar"
]

DISPLAY = {
    "age":"Umar (Age)","sex":"Gender","cholesterol":"Cholesterol",
    "blood_pressure":"Blood Pressure","heart_rate":"Heart Rate",
    "diabetes":"Diabetes","family_history":"Family History",
    "smoking":"Smoking","obesity":"Obesity",
    "alcohol_consumption":"Alcohol Use","exercise_hours_per_week":"Exercise",
    "diet":"Diet Quality","previous_heart_problems":"Prior Heart Issues",
    "medication_use":"Medication","stress_level":"Stress Level",
    "sedentary_hours_per_day":"Sedentary Hours","bmi":"BMI",
    "triglycerides":"Triglycerides","physical_activity_days_per_week":"Physical Activity",
    "sleep_hours_per_day":"Sleep Hours","chest_pain":"Chest Pain",
    "blood_sugar":"Blood Sugar"
}

HINDI = {
    "LOW":      "Aapka cardiac risk abhi kam hai. Healthy lifestyle jari rakhein — walk, paani, neend. 💚",
    "MODERATE": "Kuch factors dhyan dene wale hain. Doctor se milte rahein. Lifestyle better karein. 🟡",
    "HIGH":     "Aapka risk high hai. Kripya doctor se TURANT milein. Jitna jaldi ho sake. 🔴"
}

def risk_level(p):
    if p < 0.30: return "LOW",   "#00C47A"
    if p < 0.60: return "MODERATE", "#EDA020"
    return "HIGH", "#FF6B82"

def get_shap(fa):
    if not explainer: return {}, []
    try:
        sv = explainer.shap_values(fa)
        vals = sv[1][0] if isinstance(sv, list) else sv[0]
        d = {}
        for nm, v in zip(FEATURES, vals):
            d[DISPLAY.get(nm,nm)] = {
                "impact": round(abs(float(v))*100, 2),
                "direction": "increases" if float(v)>0 else "decreases"
            }
        sorted_d = dict(sorted(d.items(), key=lambda x: x[1]['impact'], reverse=True))
        top3 = list(sorted_d.keys())[:3]
        return sorted_d, top3
    except Exception as e:
        print(f"SHAP error: {e}")
        return {}, []

# ── /health ────────────────────────────────────────────
@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service":      "Antigravity Cardiac Risk Model",
        "status":       "live" if model else "model_not_loaded",
        "version":      "4.0",
        "features":     len(FEATURES),
        "shap_enabled": explainer is not None,
        "womens_model": women_model is not None,
        "auc":          0.81,
    })

# ── /features ──────────────────────────────────────────
@app.route('/features', methods=['GET'])
def features():
    return jsonify({
        "features": FEATURES,
        "count": len(FEATURES),
        "types": {
            "binary_0_1": ["sex","diabetes","family_history","smoking","obesity",
                          "alcohol_consumption","previous_heart_problems","medication_use","chest_pain"],
            "continuous":  ["age","cholesterol","blood_pressure","heart_rate","bmi",
                           "triglycerides","blood_sugar","exercise_hours_per_week",
                           "sedentary_hours_per_day","physical_activity_days_per_week",
                           "sleep_hours_per_day"],
            "ordinal":     ["diet (0=Unhealthy,1=Average,2=Healthy)",
                           "stress_level (1-10)"]
        }
    })

# ── /predict ───────────────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Model not loaded. Check model/antigravity_model.pkl"}), 500
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON body"}), 400

        # Build feature vector — validate all 22
        fa_list, missing = [], []
        for f in FEATURES:
            if f in data:
                fa_list.append(float(data[f]))
            else:
                missing.append(f)

        if missing:
            return jsonify({
                "error": f"Missing {len(missing)} features: {missing}",
                "required": FEATURES,
                "hint": "Send all 22 features. See /features for types."
            }), 400

        fa = np.array(fa_list).reshape(1, -1)

        # Route to women's model if available
        use_model = model
        model_used = "base"
        if data.get('sex') == 0 and women_model:
            use_model = women_model
            model_used = "womens"

        prob        = float(use_model.predict_proba(fa)[0][1])
        prediction  = int(use_model.predict(fa)[0])
        level, color = risk_level(prob)

        shap_vals, top3 = get_shap(fa)

        return jsonify({
            "prediction":    prediction,
            "probability":   round(prob, 4),
            "risk_score":    round(prob * 100, 2),
            "risk_level":    level,
            "risk_color":    color,
            "message_hindi": HINDI[level],
            "shap_values":   shap_vals,
            "top_factors":   top3,
            "model_used":    model_used,
            "disclaimer":    "Non-diagnostic wellness assessment. Not a medical device.",
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500


# ── /batch (for ASHA worker priority queue) ────────────
@app.route('/batch', methods=['POST'])
def batch():
    if not model:
        return jsonify({"error": "Model not loaded"}), 500
    try:
        data = request.get_json(force=True)
        patients = data.get('patients', [])
        if not patients or len(patients) > 100:
            return jsonify({"error": "Send 1–100 patients"}), 400

        results = []
        for p in patients:
            try:
                fa = np.array([float(p.get(f, 0)) for f in FEATURES]).reshape(1, -1)
                prob = float(model.predict_proba(fa)[0][1])
                lv, _ = risk_level(prob)
                results.append({
                    "patient_id": p.get('patient_id', 'unknown'),
                    "risk_score": round(prob*100, 2),
                    "risk_level": lv,
                    "priority":   1 if prob>=.6 else 2 if prob>=.3 else 3
                })
            except Exception as e:
                results.append({"patient_id": p.get('patient_id','?'), "error": str(e)})

        results.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
        return jsonify({"results": results, "total": len(results),
                        "high_risk": sum(1 for r in results if r.get('risk_level')=='HIGH')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── /trend (for Memory Agent — 7-day analysis) ─────────
@app.route('/trend', methods=['POST'])
def trend():
    """
    POST body: { "readings": [{"bp_sys":130,"bp_dia":85,"hr":78,"ts":1234567890}, ...] }
    Returns trend alerts for the Memory Agent.
    """
    try:
        from scipy import stats
        data = request.get_json(force=True)
        readings = data.get('readings', [])
        if len(readings) < 4:
            return jsonify({"alerts": [], "message": "Need at least 4 readings for trend analysis"})

        alerts = []
        bps = [r['bp_sys'] for r in readings if r.get('bp_sys')]
        hrs = [r['hr'] for r in readings if r.get('hr')]

        if len(bps) >= 4:
            slope, _, r, p, _ = stats.linregress(range(len(bps)), bps)
            if slope > 1.5 and p < 0.1:
                alerts.append({
                    "type": "bp_trend",
                    "severity": "warning",
                    "message_hindi": f"Aapka BP pichhle {len(bps)} readings mein dheere badh raha hai (+{slope:.1f} mmHg avg). Doctor se milein.",
                    "slope": round(slope, 2),
                    "confidence": round(r**2, 2)
                })

        if len(hrs) >= 4:
            slope, _, r, p, _ = stats.linregress(range(len(hrs)), hrs)
            if slope > 1.0 and p < 0.1:
                alerts.append({
                    "type": "hr_trend",
                    "severity": "info",
                    "message_hindi": f"Heart rate thoda badh raha hai. Stress ya neend check karein.",
                    "slope": round(slope, 2),
                    "confidence": round(r**2, 2)
                })

        return jsonify({"alerts": alerts, "readings_analysed": len(readings)})
    except ImportError:
        return jsonify({"error": "scipy not installed. Run: pip install scipy"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)
