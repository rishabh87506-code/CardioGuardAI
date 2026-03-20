"""
CardioGuardAI — Secure Proxy Server
=====================================
Deploy this to Railway.app ALONGSIDE your Antigravity model.
This server is the ONLY thing users talk to.
- Anthropic API key: never leaves this server
- Antigravity URL: never leaves this server
- Users see ZERO internal details

ENV VARS to set in Railway:
  ANTHROPIC_API_KEY    = sk-ant-api03-...
  ANTIGRAVITY_URL      = https://your-antigravity-service.railway.app
  ALLOWED_ORIGINS      = https://your-domain.com,http://localhost:8080
  PORT                 = (Railway sets this automatically)

Deploy: connect GitHub repo → Railway auto-deploys
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os, time, logging
from collections import defaultdict
from functools import wraps

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('CardioGuardAI-Proxy')

# ── Config (ALL secrets from environment — never hardcoded) ──
ANTHROPIC_KEY   = os.environ.get('ANTHROPIC_API_KEY', '')
ANTIGRAVITY_URL = os.environ.get('ANTIGRAVITY_URL', 'http://localhost:5005')
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')

CORS(app, origins=ALLOWED_ORIGINS, methods=['GET','POST','OPTIONS'],
     allow_headers=['Content-Type'])

# ── Rate limiting ─────────────────────────────────────
_rl = defaultdict(list)
def rate_limit(limit=30, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            now = time.time()
            _rl[ip] = [t for t in _rl[ip] if t > now - window]
            if len(_rl[ip]) >= limit:
                return jsonify({"error": "Bahut zyada requests. Thodi der mein dobara try karein."}), 429
            _rl[ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ── Health check ──────────────────────────────────────
@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service":   "CardioGuardAI Proxy",
        "status":    "live",
        "version":   "4.0",
        "claude_ok": bool(ANTHROPIC_KEY),
        "ag_ok":     bool(ANTIGRAVITY_URL),
        # Never expose actual keys or URLs
    })

# ── /api/chat — proxies Claude, key hidden ────────────
@app.route('/api/chat', methods=['POST', 'OPTIONS'])
@rate_limit(30, 60)
def chat():
    if request.method == 'OPTIONS': return '', 204
    if not ANTHROPIC_KEY:
        return jsonify({"error": "Service not configured"}), 503
    try:
        body = request.get_json(force=True)
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type':      'application/json',
                'x-api-key':         ANTHROPIC_KEY,   # Key NEVER leaves proxy
                'anthropic-version': '2023-06-01',
            },
            json={
                'model':      body.get('model', 'claude-sonnet-4-20250514'),
                'max_tokens': min(int(body.get('max_tokens', 1024)), 2048),
                'system':     body.get('system', ''),
                'messages':   body.get('messages', []),
            },
            timeout=30
        )
        data = resp.json()
        if 'error' in data:
            safe = {
                'authentication_error': 'Service configuration error.',
                'rate_limit_error':     'Bahut zyada requests. Thodi der mein dobara try karein.',
                'overloaded_error':     'Service thodi busy hai. Dobara try karein.',
            }.get(data['error'].get('type'), 'Service temporarily unavailable.')
            return jsonify({"error": safe}), resp.status_code
        return jsonify(data)
    except requests.Timeout:
        return jsonify({"error": "Response timeout. Dobara try karein."}), 504
    except Exception as e:
        log.error(f"Chat error: {e}")
        return jsonify({"error": "Service error."}), 500

# ── /api/predict — proxies Antigravity, URL hidden ────
@app.route('/api/predict', methods=['POST', 'OPTIONS'])
@rate_limit(20, 60)
def predict():
    if request.method == 'OPTIONS': return '', 204
    if not ANTIGRAVITY_URL:
        return jsonify({"error": "Antigravity model not connected yet.", "status": "not_configured"}), 503
    try:
        body = request.get_json(force=True)
        resp = requests.post(
            f"{ANTIGRAVITY_URL.rstrip('/')}/predict",
            headers={'Content-Type': 'application/json'},
            json=body, timeout=15
        )
        data = resp.json()
        # Normalise response — remove any internal model metadata
        data.pop('model_version', None)
        data.pop('model_path', None)
        data.pop('training_data', None)
        return jsonify(data)
    except requests.ConnectionError:
        return jsonify({"error": "Antigravity model unreachable."}), 503
    except Exception as e:
        log.error(f"Predict error: {e}")
        return jsonify({"error": "Prediction service error."}), 500

# ── /api/analyse — image report analysis ─────────────
@app.route('/api/analyse', methods=['POST', 'OPTIONS'])
@rate_limit(10, 60)
def analyse():
    if request.method == 'OPTIONS': return '', 204
    if not ANTHROPIC_KEY:
        return jsonify({"error": "Service not configured"}), 503
    import base64
    try:
        f = request.files.get('file')
        rtype = request.form.get('type', 'lab')
        if not f: return jsonify({"error": "No file"}), 400
        if f.content_type not in ['image/jpeg','image/png','image/webp']:
            return jsonify({"error": "Only JPEG/PNG/WebP images"}), 400
        data = f.read()
        if len(data) > 5_000_000: return jsonify({"error": "File too large (max 5MB)"}), 413
        b64 = base64.b64encode(data).decode()
        prompts = {
            'lab':  'Lab report explain karo Hinglish mein. Normal (✓) aur abnormal (⚠) values mark karo. Cardiac relevance batao.',
            'ecg':  'ECG patterns describe karo simple Hinglish mein. Always recommend cardiologist review.',
            'echo': 'Echo report mein EF, wall motion, valves explain karo simple Hinglish mein.',
            'rx':   'Prescription ki dawaiyan list karo aur common uses batao. Doses kabhi suggest mat karo.',
        }
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={'Content-Type':'application/json','x-api-key':ANTHROPIC_KEY,'anthropic-version':'2023-06-01'},
            json={'model':'claude-sonnet-4-20250514','max_tokens':1024,
                  'system':'You are Hridai, CardioGuardAI ka Master Agent. Explain medical reports in warm Hinglish. Always end with ⚠ Doctor se zaroor milein.',
                  'messages':[{'role':'user','content':[
                      {'type':'image','source':{'type':'base64','media_type':f.content_type,'data':b64}},
                      {'type':'text','text':prompts.get(rtype,prompts['lab'])}
                  ]}]},
            timeout=30
        )
        reply = resp.json().get('content',[{}])[0].get('text','Report analyse nahi ho payi.')
        return jsonify({"analysis":reply,"type":rtype})
    except Exception as e:
        log.error(f"Analyse error: {e}")
        return jsonify({"error": "Analysis failed."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5006))
    app.run(host='0.0.0.0', port=port, debug=False)
