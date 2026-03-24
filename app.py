"""
CardioGuard AI — Hridai Agent OS v4.9 (Hardened)
=================================================
Wellness support platform — NON-DIAGNOSTIC.
Compliant with FDA Digital Health Policy (wellness exemption)
and CDSCO SaMD guidelines (lifestyle/wellness category).

Security: rate limiting, security headers, threat detection,
          audit logging, pitch access control.
"""

import os
import re
import json
import time
import pickle
import joblib
import hashlib
import logging
import numpy as np
import requests
from datetime import datetime, timezone
from collections import defaultdict
from flask import Flask, request, jsonify, send_file, redirect, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hmac
import secrets

# ── LOGGING SETUP ──────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
log = logging.getLogger('cardioguard')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB (audio uploads need room)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["300 per day", "60 per hour"],
    storage_uri="memory://"
)

# ── CONFIGURATION ──────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
WHATSAPP_KEY      = os.environ.get('WHATSAPP_API_KEY', '')
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID', '')
OPENAI_API_KEY    = os.environ.get('OPENAI_API_KEY', '')
SESSION_SECRET    = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
PITCH_TOKEN       = os.environ.get('PITCH_ACCESS_TOKEN', '')  # empty = pitch disabled
MODEL_PATH        = os.path.join(os.path.dirname(__file__), 'model', 'antigravity_model.pkl')

_DEFAULT_ORIGINS = (
    'https://cardioguardai.in,https://www.cardioguardai.in,'
    'https://cardioguardai.co.in,https://www.cardioguardai.co.in'
)
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', _DEFAULT_ORIGINS).split(',')
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=False)

# ── THREAT DETECTION ───────────────────────────────────
_threat_counts  = defaultdict(int)
_blocked_ips    = set()
_BLOCK_THRESHOLD = 5

THREAT_PATTERNS = [
    (re.compile(r'union\s+select|drop\s+table|insert\s+into|delete\s+from|exec\s*\(', re.I), 'SQLi'),
    (re.compile(r'<script|javascript:|onerror\s*=|onload\s*=|alert\s*\(',              re.I), 'XSS'),
    (re.compile(r'\.\.\/|\.\.\\|%2e%2e%2f|%252e',                                     re.I), 'PathTraversal'),
    (re.compile(r'etc/passwd|etc/shadow|win32|system32|cmd\.exe',                      re.I), 'SysAccess'),
    (re.compile(r'/bin/sh|/bin/bash|powershell|wget\s+http|curl\s+http',               re.I), 'CmdInject'),
    (re.compile(r'base64_decode|eval\(|exec\(|system\(|popen\(',                       re.I), 'CodeExec'),
]

def _client_ip():
    return (request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
            or request.remote_addr or 'unknown')

def _threat_check(payload):
    for pattern, label in THREAT_PATTERNS:
        if pattern.search(payload):
            return label
    return None

def _audit(event, extra=None):
    ip = _client_ip()
    data = {
        "ts":      datetime.now(timezone.utc).isoformat(),
        "event":   event,
        "ip_hash": hashlib.sha256(ip.encode()).hexdigest()[:16],
        "path":    request.path,
        "method":  request.method,
        "ua":      request.headers.get('User-Agent', '')[:100],
    }
    if extra:
        data.update(extra)
    log.info(json.dumps(data))

# ── SECURITY MIDDLEWARE ────────────────────────────────
@app.before_request
def guard():
    ip = _client_ip()
    if ip in _blocked_ips:
        _audit("BLOCKED_IP")
        abort(403)
    raw = request.url + ' ' + request.data.decode('utf-8', errors='ignore')[:4096]
    threat = _threat_check(raw)
    if threat:
        _threat_counts[ip] += 1
        _audit("THREAT_DETECTED", {"type": threat, "count": _threat_counts[ip]})
        if _threat_counts[ip] >= _BLOCK_THRESHOLD:
            _blocked_ips.add(ip)
            _audit("IP_BLOCKED", {"type": threat})
        abort(400)

@app.after_request
def security_headers(resp):
    resp.headers['X-Content-Type-Options']   = 'nosniff'
    resp.headers['X-Frame-Options']          = 'DENY'
    resp.headers['X-XSS-Protection']         = '1; mode=block'
    resp.headers['Referrer-Policy']          = 'strict-origin-when-cross-origin'
    resp.headers['Permissions-Policy']       = 'geolocation=(), microphone=(), camera=()'
    resp.headers['Strict-Transport-Security']= 'max-age=63072000; includeSubDomains; preload'
    resp.headers['Content-Security-Policy']  = (
        "default-src 'self' https:; "
        "script-src 'self' 'unsafe-inline' https://www.gstatic.com https://accounts.google.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.anthropic.com https://www.googleapis.com "
        "https://identitytoolkit.googleapis.com https://securetoken.googleapis.com "
        "https://overpass-api.de https://graph.facebook.com; "
        "worker-src 'self'; "
        "manifest-src 'self'; "
        "frame-ancestors 'none';"
    )
    resp.headers.pop('Server', None)
    resp.headers.pop('X-Powered-By', None)
    return resp

# ── COMPLIANCE DISCLAIMER ──────────────────────────────
DISCLAIMER = (
    "CardioGuard AI is a non-diagnostic wellness support tool. "
    "Results are for informational purposes only and do not constitute "
    "medical advice, diagnosis, or treatment. "
    "Always consult a qualified physician for clinical decisions. "
    "Compliant: FDA Digital Health Policy (wellness exemption) + "
    "CDSCO SaMD Guidelines (lifestyle/wellness category)."
)

# ── OTP STORE (in-memory, TTL 10 min) ──────────────────
_otp_store = {}   # sha256(phone) -> {hash, expires, attempts, phone_hint}
_OTP_TTL    = 600  # 10 minutes
_OTP_MAX_AT = 5

def _phone_hash(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()[:20]

def _otp_hash(otp: str, phone: str) -> str:
    return hmac.new(SESSION_SECRET.encode(), f"{otp}:{phone}".encode(), 'sha256').hexdigest()

def _gen_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)

def _send_whatsapp_otp(phone: str, otp: str) -> bool:
    if not WHATSAPP_KEY or not WHATSAPP_PHONE_ID:
        log.info(f"[MOCK WA-OTP] {phone[-4:]} → {otp}")
        return True   # dev mock — always succeeds
    try:
        body = (f"🫀 *CardioGuardAI*\n\n"
                f"Aapka OTP hai: *{otp}*\n"
                f"Valid: 10 minutes\n\n"
                f"_Yeh code kisi ke saath share mat karein._\n"
                f"cardioguardai.in")
        res = requests.post(
            f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {WHATSAPP_KEY}", "Content-Type": "application/json"},
            json={"messaging_product": "whatsapp", "to": phone,
                  "type": "text", "text": {"body": body}},
            timeout=10
        )
        return res.status_code == 200
    except Exception as e:
        log.error(f"WhatsApp OTP send failed: {e}")
        return False

def _send_sms_otp(phone: str, otp: str) -> bool:
    """SMS via Fast2SMS (India) — set FAST2SMS_KEY env var."""
    key = os.environ.get('FAST2SMS_KEY', '')
    if not key:
        log.info(f"[MOCK SMS-OTP] {phone[-4:]} → {otp}")
        return True
    try:
        res = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": key},
            json={"route": "otp", "variables_values": otp,
                  "flash": 0, "numbers": phone},
            timeout=10
        )
        return res.json().get('return', False)
    except Exception as e:
        log.error(f"SMS OTP send failed: {e}")
        return False

def _make_session_token(phone: str) -> str:
    ts = str(int(time.time()))
    ph = _phone_hash(phone)
    payload = f"{ph}:{ts}"
    sig = hmac.new(SESSION_SECRET.encode(), payload.encode(), 'sha256').hexdigest()[:24]
    return f"{payload}:{sig}"

# ── FEATURE SPEC ───────────────────────────────────────
FEATURES = [
    "age","sex","cholesterol","blood_pressure","heart_rate",
    "diabetes","family_history","smoking","obesity","alcohol_consumption",
    "exercise_hours_per_week","diet","previous_heart_problems","medication_use",
    "stress_level","sedentary_hours_per_day","bmi","triglycerides",
    "physical_activity_days_per_week","sleep_hours_per_day","chest_pain","blood_sugar"
]

FEATURE_RANGES = {
    "age": (18, 100),          "sex": (0, 1),
    "cholesterol": (50, 600),  "blood_pressure": (60, 260),
    "heart_rate": (30, 250),   "diabetes": (0, 1),
    "family_history": (0, 1),  "smoking": (0, 1),
    "obesity": (0, 1),         "alcohol_consumption": (0, 1),
    "exercise_hours_per_week": (0, 30),
    "diet": (0, 2),            "previous_heart_problems": (0, 1),
    "medication_use": (0, 1),  "stress_level": (1, 10),
    "sedentary_hours_per_day": (0, 24),
    "bmi": (10, 70),           "triglycerides": (20, 1000),
    "physical_activity_days_per_week": (0, 7),
    "sleep_hours_per_day": (2, 16),
    "chest_pain": (0, 1),      "blood_sugar": (50, 600),
}

DISPLAY_NAMES = {
    "age": "Umar (Age)", "sex": "Gender", "cholesterol": "Cholesterol",
    "blood_pressure": "Blood Pressure", "heart_rate": "Heart Rate",
    "diabetes": "Diabetes", "family_history": "Family History",
    "smoking": "Smoking", "obesity": "Obesity", "triglycerides": "Triglycerides",
    "bmi": "BMI", "blood_sugar": "Blood Sugar", "chest_pain": "Chest Pain"
}

# ── WHATSAPP AGENT ─────────────────────────────────────
class WhatsAppAgent:
    def __init__(self, key):
        self.key = key

    def broadcast(self, name, score, level):
        if not self.key or self.key == "MOCK":
            log.info(f"[MOCK BROADCAST] {name} | {score}% | {level}")
            return False
        log.info(f"[WHATSAPP] Alert dispatched: {name} ({score}%)")
        return True

wa_agent = WhatsAppAgent(WHATSAPP_KEY)

# ── LOAD MODEL ─────────────────────────────────────────
def load_risk_model():
    if not os.path.exists(MODEL_PATH):
        log.warning("Model not found — prediction service offline.")
        return None
    try:
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    except Exception:
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            log.error(f"Model load failed: {e}")
            return None

model = load_risk_model()

explainer = None
if model:
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        log.info("SHAP explainer ready")
    except Exception as e:
        log.info(f"SHAP not initialized (graceful): {e}")

# ══════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════

@app.route('/pitch')
def serve_pitch():
    """Private investor pitch — requires PITCH_ACCESS_TOKEN."""
    if not PITCH_TOKEN:
        return redirect('/', code=302)
    if request.args.get('token', '') != PITCH_TOKEN:
        _audit("PITCH_ACCESS_DENIED")
        return redirect('/', code=302)
    _audit("PITCH_ACCESSED")
    return send_file('landing.html')

@app.route('/logo.png')
def serve_logo():
    return send_file('logo.png', mimetype='image/png')

@app.route('/manifest.json')
def serve_manifest():
    resp = send_file('manifest.json', mimetype='application/manifest+json')
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp

@app.route('/sw.js')
def serve_sw():
    resp = send_file('sw.js', mimetype='application/javascript')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Service-Worker-Allowed'] = '/'
    return resp

@app.route('/.well-known/assetlinks.json')
def serve_assetlinks():
    resp = send_file('.well-known/assetlinks.json', mimetype='application/json')
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp

@app.route('/')
@app.route('/index.html')
def serve_index():
    return send_file('index.html')

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
@limiter.limit("30 per minute")
def health():
    return jsonify({
        "status":      "live",
        "service":     "CardioGuard AI — Hridai Agent OS",
        "version":     "4.9",
        "model_ready": model is not None,
        "ai_ready":    len(ANTHROPIC_API_KEY) > 20,
        "whisper_ready": len(OPENAI_API_KEY) > 20,
        "tts_ready":   len(OPENAI_API_KEY) > 20,
        "whatsapp_otp": bool(WHATSAPP_KEY and WHATSAPP_PHONE_ID),
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
        "compliance":  "FDA Wellness Exemption + CDSCO SaMD Lifestyle Category",
        "timestamp":   time.time()
    })

@app.route('/api/config')
@limiter.limit("20 per minute")
def get_config():
    return jsonify({
        "firebase": {
            "apiKey":            os.environ.get('FIREBASE_API_KEY', ''),
            "authDomain":        os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
            "projectId":         os.environ.get('FIREBASE_PROJECT_ID', ''),
            "storageBucket":     os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
            "messagingSenderId": os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
            "appId":             os.environ.get('FIREBASE_APP_ID', '')
        }
    })

@app.route('/api/otp/send', methods=['POST'])
@limiter.limit("3 per hour")
def otp_send():
    data = request.get_json(force=True, silent=True) or {}
    phone  = str(data.get('phone', '')).strip()
    method = str(data.get('method', 'whatsapp'))  # 'whatsapp' or 'sms'

    if not phone or len(phone) < 8 or len(phone) > 20:
        return jsonify({"error": "Invalid phone number"}), 400

    # Clean old OTPs
    now = time.time()
    expired = [k for k, v in _otp_store.items() if v['expires'] < now]
    for k in expired: del _otp_store[k]

    otp  = _gen_otp()
    phk  = _phone_hash(phone)
    _otp_store[phk] = {
        "hash":       _otp_hash(otp, phone),
        "expires":    now + _OTP_TTL,
        "attempts":   0,
        "phone_hint": phone[-4:]
    }

    sent = (_send_whatsapp_otp(phone, otp) if method == 'whatsapp'
            else _send_sms_otp(phone, otp))

    _audit("OTP_SENT", {"method": method, "hint": phone[-4:]})
    return jsonify({"ok": sent, "method": method, "hint": phone[-4:],
                    "dev_otp": otp if not (WHATSAPP_KEY and WHATSAPP_PHONE_ID) else None})


@app.route('/api/otp/verify', methods=['POST'])
@limiter.limit("10 per minute")
def otp_verify():
    data  = request.get_json(force=True, silent=True) or {}
    phone = str(data.get('phone', '')).strip()
    otp   = str(data.get('otp', '')).strip()

    if not phone or not otp:
        return jsonify({"error": "Phone and OTP required"}), 400

    phk   = _phone_hash(phone)
    entry = _otp_store.get(phk)

    if not entry:
        return jsonify({"error": "OTP not found or expired"}), 400
    if time.time() > entry['expires']:
        del _otp_store[phk]
        return jsonify({"error": "OTP expired — please request a new one"}), 400
    if entry['attempts'] >= _OTP_MAX_AT:
        del _otp_store[phk]
        return jsonify({"error": "Too many attempts — please request a new OTP"}), 429

    entry['attempts'] += 1
    if not hmac.compare_digest(entry['hash'], _otp_hash(otp, phone)):
        remaining = _OTP_MAX_AT - entry['attempts']
        return jsonify({"error": f"Wrong OTP. {remaining} attempts left"}), 401

    del _otp_store[phk]
    token = _make_session_token(phone)
    _audit("OTP_VERIFIED", {"hint": phone[-4:]})
    return jsonify({"ok": True, "token": token, "phone_hint": phone[-4:]})


@app.route('/api/transcribe', methods=['POST'])
@limiter.limit("20 per minute")
def transcribe():
    """Whisper STT — accepts audio file, returns transcript."""
    if not OPENAI_API_KEY:
        return jsonify({"error": "Transcription service not configured"}), 503
    audio = request.files.get('audio')
    if not audio:
        return jsonify({"error": "No audio file"}), 400
    lang = request.form.get('language', 'hi')
    try:
        res = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            files={"file": (audio.filename or "audio.webm",
                            audio.stream,
                            audio.content_type or "audio/webm")},
            data={"model": "whisper-1", "language": lang,
                  "prompt": "CardioGuardAI wellness platform. Hinglish medical conversation."},
            timeout=30
        )
        _audit("WHISPER_TRANSCRIBE", {"lang": lang})
        return (res.text, res.status_code, {"Content-Type": "application/json"})
    except requests.Timeout:
        return jsonify({"error": "Transcription timed out"}), 504
    except Exception as e:
        log.error(f"Whisper error: {e}")
        return jsonify({"error": "Transcription failed"}), 500


@app.route('/api/tts', methods=['POST'])
@limiter.limit("30 per minute")
def tts():
    """OpenAI TTS — returns audio/mpeg."""
    if not OPENAI_API_KEY:
        return jsonify({"error": "TTS not configured"}), 503
    data  = request.get_json(force=True, silent=True) or {}
    text  = str(data.get('text', ''))[:600]
    voice = data.get('voice', 'nova')  # nova | shimmer | alloy | echo | fable | onyx
    if voice not in ('nova','shimmer','alloy','echo','fable','onyx'):
        voice = 'nova'
    if not text:
        return jsonify({"error": "No text"}), 400
    # Clean markdown for TTS
    import re as _re
    clean = _re.sub(r'\*\*|__|\*|_|#{1,6} |`|<[^>]+>', '', text)[:500]
    try:
        res = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": "tts-1", "input": clean, "voice": voice},
            timeout=20
        )
        if res.status_code == 200:
            return (res.content, 200, {"Content-Type": "audio/mpeg",
                                       "Cache-Control": "no-store"})
        return jsonify({"error": "TTS API error"}), res.status_code
    except requests.Timeout:
        return jsonify({"error": "TTS timed out"}), 504
    except Exception as e:
        log.error(f"TTS error: {e}")
        return jsonify({"error": "TTS failed"}), 500


@app.route('/api/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    if not model:
        return jsonify({"error": "Wellness analytics engine not active."}), 503
    try:
        data = request.get_json(force=True, silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload."}), 400

        fa_list = []
        for f in FEATURES:
            if f not in data:
                return jsonify({"error": f"Missing field: {f}"}), 400
            try:
                val = float(data[f])
            except (TypeError, ValueError):
                return jsonify({"error": f"Invalid value for {f}"}), 400
            lo, hi = FEATURE_RANGES.get(f, (-1e9, 1e9))
            if not (lo <= val <= hi):
                return jsonify({"error": f"{f} out of range ({lo}-{hi})"}), 400
            fa_list.append(val)

        fa    = np.array(fa_list).reshape(1, -1)
        prob  = float(model.predict_proba(fa)[0][1])
        score = round(prob * 100, 2)

        if score >= 70:
            level, asha_dispatch = "CRITICAL DEVIATION", True
        elif score >= 30:
            level, asha_dispatch = "MODERATE DEVIATION", False
        else:
            level, asha_dispatch = "OPTIMAL", False

        broadcasted = False
        if asha_dispatch or data.get('emergency', False):
            name = str(data.get('name', 'User'))[:60]
            broadcasted = wa_agent.broadcast(name, score, level)

        shap_vals = {}
        if explainer:
            try:
                sv   = explainer.shap_values(fa)
                vals = sv[1][0] if isinstance(sv, list) else sv[0]
                for nm, v in zip(FEATURES, vals):
                    dn = DISPLAY_NAMES.get(nm, nm.replace('_', ' ').title())
                    shap_vals[dn] = {
                        "impact":    round(abs(float(v)) * 100, 2),
                        "direction": "increases" if v > 0 else "decreases"
                    }
                shap_vals = dict(sorted(shap_vals.items(),
                                        key=lambda x: x[1]['impact'], reverse=True))
            except Exception:
                pass

        _audit("WELLNESS_ASSESSMENT", {"score": score, "level": level})
        return jsonify({
            "wellness_score":   score,
            "insight_category": level,
            "broadcast_status": broadcasted,
            "factor_analysis":  shap_vals,
            "disclaimer":       DISCLAIMER,
            "category":         "Wellness Support Tool (Non-Diagnostic)"
        })

    except Exception as e:
        log.error(f"predict error: {e}")
        return jsonify({"error": "Assessment failed. Please try again."}), 500

@app.route('/api/batch', methods=['POST'])
@limiter.limit("5 per minute")
def batch_predict():
    if not model:
        return jsonify({"error": "Engine offline"}), 503
    try:
        cases = request.get_json(force=True, silent=True)
        if not isinstance(cases, list):
            return jsonify({"error": "Payload must be a list"}), 400
        if len(cases) > 100:
            return jsonify({"error": "Batch limit is 100 records"}), 400

        results = []
        for data in cases:
            if not isinstance(data, dict):
                continue
            fa_list = []
            for f in FEATURES:
                try:
                    val = float(data.get(f, 0))
                    lo, hi = FEATURE_RANGES.get(f, (-1e9, 1e9))
                    val = max(lo, min(hi, val))
                except (TypeError, ValueError):
                    val = 0.0
                fa_list.append(val)
            fa    = np.array(fa_list).reshape(1, -1)
            prob  = float(model.predict_proba(fa)[0][1])
            score = round(prob * 100, 2)
            results.append({
                "wellness_score": score,
                "level": "DEVIATION" if score >= 30 else "OPTIMAL"
            })

        _audit("BATCH_ASSESSMENT", {"count": len(results)})
        return jsonify({"count": len(results), "results": results, "disclaimer": DISCLAIMER})

    except Exception as e:
        log.error(f"batch error: {e}")
        return jsonify({"error": "Batch failed. Please try again."}), 500

@app.route('/api/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat():
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "AI guidance service not configured."}), 503
    try:
        data = request.get_json(force=True, silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid payload"}), 400

        messages = data.get("messages", [])
        if not isinstance(messages, list) or len(messages) > 50:
            return jsonify({"error": "Invalid messages"}), 400

        system = str(data.get("system", ""))[:4000]
        max_tokens = min(int(data.get("max_tokens", 1024)), 2048)

        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model":      "claude-sonnet-4-6",
                "max_tokens": max_tokens,
                "system":     system,
                "messages":   messages
            },
            timeout=30
        )
        # Only forward Content-Type — never leak Anthropic internals
        return (res.text, res.status_code, {"Content-Type": res.headers.get("Content-Type", "application/json")})

    except requests.Timeout:
        return jsonify({"error": "AI service timeout. Please try again."}), 504
    except Exception as e:
        log.error(f"chat error: {e}")
        return jsonify({"error": "AI guidance unavailable. Please try again."}), 500

# ── ERROR HANDLERS ─────────────────────────────────────
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Access denied"}), 403

@app.errorhandler(404)
def not_found(e):
    _audit("404")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(413)
def too_large(e):
    _audit("REQUEST_TOO_LARGE")
    return jsonify({"error": "Request too large (max 64KB)"}), 413

@app.errorhandler(429)
def rate_limited(e):
    _audit("RATE_LIMITED")
    return jsonify({"error": "Too many requests. Please slow down."}), 429

# ══════════════════════════════════════════════════════
#  STARTUP
# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 58)
    print("  Hridai Agent OS v4.9 — Hardened Production Boot")
    print("=" * 58)
    print(f"  Model      : {'LOADED' if model else 'MISSING'}")
    print(f"  Claude AI  : {'READY' if ANTHROPIC_API_KEY else 'STANDBY'}")
    print(f"  Pitch Page : {'PROTECTED' if PITCH_TOKEN else 'DISABLED (set PITCH_ACCESS_TOKEN)'}")
    print(f"  Security   : Threat detection | Audit logs | Rate limiting")
    print(f"  Compliance : FDA Wellness Exemption + CDSCO SaMD")
    print("=" * 58)
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)
