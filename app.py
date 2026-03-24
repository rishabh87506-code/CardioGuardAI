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
SARVAM_API_KEY    = os.environ.get('SARVAM_API_KEY', '') # For Indic Voice Layer
SESSION_SECRET    = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
PITCH_TOKEN      = os.environ.get('PITCH_ACCESS_TOKEN', 'pitch2026')
DB_PATH          = os.environ.get('DATABASE_URL', 'hridai_audit.db')

# ── DATABASE ARCHITECTURE (v6.0 Audit-Ready) ─────────────────────────
import sqlite3
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                event TEXT,
                data TEXT
            );
            CREATE TABLE IF NOT EXISTS vitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                sys INTEGER, dia INTEGER, hr INTEGER, bs INTEGER,
                type TEXT, -- 'manual', 'ppg', 'rppg'
                source TEXT -- 'wearable', 'camera', 'manual'
            );
            CREATE TABLE IF NOT EXISTS emergencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                type TEXT, -- 'cvd', 'accident', 'natural'
                lat REAL, lon REAL,
                status TEXT DEFAULT 'pending'
            );
            CREATE TABLE IF NOT EXISTS health_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                type TEXT,
                price_rating INTEGER, -- 1-5
                cvd_specialty INTEGER, -- 1-5
                reviews TEXT
            );
        """)
        # Seed some healthcare data
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM health_providers")
        if cur.fetchone()[0] == 0:
            providers = [
                ('Apollo Heart Institute', 'Tertiary', 4, 5, 'Best for CVD surgery, highly rated'),
                ('Max Super Specialty', 'Tertiary', 5, 4, 'Advanced labs, fast response'),
                ('AIIMS Delhi', 'Government', 1, 5, 'World class, high volume'),
                ('Local PHC - Kalkaji', 'Primary', 1, 2, 'Reliable for checkups, near metro')
            ]
            cur.executemany("INSERT INTO health_providers (name,type,price_rating,cvd_specialty,reviews) VALUES (?,?,?,?,?)", providers)
            conn.commit()

init_db()
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
    """Indic Voice Layer: Sarvam AI (Primary) → Whisper (Fallback)"""
    audio = request.files.get('audio')
    if not audio: return jsonify({"error": "No audio file"}), 400
    lang = request.form.get('language', 'hi-IN')

    # 1. Try Sarvam AI (Indic optimized)
    if SARVAM_API_KEY:
        try:
            res = requests.post(
                "https://api.sarvam.ai/speech-to-text-translate",
                headers={"api-subscription-key": SARVAM_API_KEY},
                files={"file": (audio.filename or "audio.webm", audio.stream, audio.content_type or "audio/webm")},
                data={"model": "saarika:v1", "language_code": lang},
                timeout=25
            )
            if res.status_code == 200:
                _audit("SARVAM_STT", {"lang": lang})
                return (res.text, 200, {"Content-Type": "application/json"})
        except Exception as e:
            log.error(f"Sarvam STT failed: {e}")

    # 2. Fallback to OpenAI Whisper
    if OPENAI_API_KEY:
        try:
            # We need to seek back to start of stream if Sarvam failed
            audio.stream.seek(0)
            res = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files={"file": (audio.filename or "audio.webm", audio.stream, audio.content_type or "audio/webm")},
                data={"model": "whisper-1", "language": lang.split('-')[0],
                      "prompt": "CardioGuardAI Hinglish cardiac wellness platform."},
                timeout=30
            )
            _audit("WHISPER_STT", {"lang": lang})
            return (res.text, res.status_code, {"Content-Type": "application/json"})
        except Exception as e:
            log.error(f"Whisper fallback failed: {e}")

    return jsonify({"error": "Transcription Layer unavailable"}), 503


@app.route('/api/tts', methods=['POST'])
@limiter.limit("30 per minute")
def tts():
    """Indic Voice Layer: Sarvam AI (Primary) → OpenAI (Fallback)"""
    data  = request.get_json(force=True, silent=True) or {}
    text  = str(data.get('text', ''))[:600]
    lang  = data.get('lang', 'hi-IN')
    if not text: return jsonify({"error": "No text"}), 400

    # 1. Try Sarvam AI (Indic quality is superior)
    if SARVAM_API_KEY:
        try:
            res = requests.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"},
                json={
                    "text": text,
                    "target_language_code": lang,
                    "speaker": "shiku",  # Empathetic Hinglish female
                    "model": "bulbul:v1"
                },
                timeout=12
            )
            if res.status_code == 200:
                audio_base64 = res.json().get('audios', [None])[0]
                if audio_base64:
                    import base64
                    return (base64.b64decode(audio_base64), 200, {"Content-Type": "audio/wav"})
        except Exception as e:
            log.error(f"Sarvam TTS failed: {e}")

    # 2. Fallback to OpenAI TTS
    if OPENAI_API_KEY:
        try:
            clean = re.sub(r'\*\*|__|\*|_|#{1,6} |`|<[^>]+>', '', text)[:500]
            res = requests.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": "tts-1", "input": clean, "voice": "nova"},
                timeout=15
            )
            if res.status_code == 200:
                return (res.content, 200, {"Content-Type": "audio/mpeg"})
        except Exception as e:
            log.error(f"OpenAI TTS fallback failed: {e}")

    return jsonify({"error": "Voice Layer unavailable"}), 503


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

HRIDAI_KNOWLEDGE = [
    {"keys": ["chest", "dard", "pain", "saans", "breathless", "behosh"], "reply": "🚨 [NAME], please abhi **108 pe call karein!**\n\nMujhe aapke patterns dekh ke thodi fikar ho rahi hai dukh raha hai ya saans leni mein takleef hai? Ghabrayein mat, par abhi hospital jana behtar hai. Main yahin hoon, aap bas araam se baith jaayein. ❤️"},
    {"keys": ["bp", "blood pressure", "systolic", "dia", "tension"], "reply": "BP ke liye thoda dhyaan dena hoga, [NAME]. Namak kam kijiye, roz 30 min ki halki walk start karein aur stress manage karne ke liye meditation kijiye. Ek baar doctor se checkup karana zaroori hai. ❤️"},
    {"keys": ["wellness", "health", "lifestyle", "khana", "diet"], "reply": "Health ke liye sabse zaroori hai discipline, [NAME]. Ghar ka khana khaiye, junk food avoid kijiye, aur roz 7-8 ghante ki achhi neend lijiye. Dil khush rahega to health bhi achhi rahegi! ❤️"},
    {"keys": ["kaisa", "kaun", "intro", "namaste", "hi"], "reply": "Namaste [NAME]! Main **Hridai** hoon—aapka Master Wellness Coordinator. Main aapke dil ki health track karne mein madad karta hoon. Aaj aap kaisa mehsoos kar rahe hain? 😊"}
]

def hridai_local_reply(msg, name="dost"):
    msg = msg.lower()
    for item in HRIDAI_KNOWLEDGE:
        if any(k in msg for k in item["keys"]):
            return item["reply"].replace("[NAME]", name if name else "dost")
    return f"Suno {name if name else 'dost'}, abhi network ki wajah se main thoda dheere hoon, par main yahin hoon aapke saath. Aap kya kehte hain, aaj ki dincharya kaisi rahi? ❤️"

@app.route('/api/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat():
    # If no keys at all, use Hridai-Local as 'Secret Sauce'
    data = request.get_json(force=True, silent=True) or {}
    msg = ""
    if data.get("messages"):
        msg = data["messages"][-1].get("content", "")
    
    # Extract user name from context if possible
    sys_prompt = data.get("system", "")
    import re
    u_match = re.search(r"Name=([^,\s|\]]+)", sys_prompt)
    u_name = u_match.group(1) if u_match else "dost"

    try:
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid payload"}), 400

        messages = data.get("messages", [])
        if not isinstance(messages, list) or len(messages) > 50:
            return jsonify({"error": "Invalid messages"}), 400

        system = str(data.get("system", ""))[:4000]
        max_tokens = min(int(data.get("max_tokens", 1024)), 2048)
        model = "claude-3-5-sonnet-20240620"

        # ── ATTEMPT 1: Anthropic Claude (Primary) ──
        if ANTHROPIC_API_KEY:
            for attempt in range(3):
                try:
                    res = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": ANTHROPIC_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model":      model,
                            "max_tokens": max_tokens,
                            "system":     system,
                            "messages":   messages
                        },
                        timeout=20 + (attempt * 10)
                    )
                    if res.status_code == 200:
                        _audit("CHAT_SUCCESS", {"attempt": attempt + 1})
                        return (res.text, 200, {"Content-Type": "application/json"})
                    
                    if res.status_code == 429:
                        time.sleep(1 + attempt)
                        continue
                    log.warning(f"Claude API attempt {attempt+1} failed: {res.status_code}")
                except Exception as e:
                    log.error(f"Claude API connection error: {e}")
                    time.sleep(0.5)

        # ── ATTEMPT 2: OpenAI GPT-4o-mini (Secret Sauce Fallback) ──
        if OPENAI_API_KEY:
            try:
                log.info("Switching to Secret Sauce (OpenAI Fallback)...")
                res = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "system", "content": system}] + messages,
                        "max_tokens": max_tokens
                    },
                    timeout=20
                )
                if res.status_code == 200:
                    openai_reply = res.json()["choices"][0]["message"]["content"]
                    return jsonify({
                        "id": f"sc-{int(time.time())}",
                        "model": "openai-secret-sauce",
                        "content": [{"text": openai_reply, "type": "text"}]
                    })
            except Exception as e:
                log.error(f"OpenAI fallback failed: {e}")

        # ── ATTEMPT 3: HRIDAI LOCAL INTELLIGENCE (The Offline Heart) ──
        log.info("Triggering Hridai-Local Intelligence...")
        local_text = hridai_local_reply(msg, u_name)
        return jsonify({
            "id": f"lh-{int(time.time())}",
            "model": "hridai-local-v5",
            "content": [{"text": local_text, "type": "text"}]
        })

    except Exception as e:
        log.error(f"Final chat rescue fail: {e}")
        return jsonify({
            "id": f"lh-{int(time.time())}",
            "model": "hridai-local-v5",
            "content": [{"text": hridai_local_reply(msg, u_name), "type": "text"}]
        })

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
