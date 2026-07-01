# app.py
import os
import secrets
import logging
from flask import Flask, request, jsonify, render_template, session as flask_session, abort

from config.specialties import GLOBAL_BASELINE_FEATURES, SPECIALTY_FIELDS
from config.advice import SPECIALTY_ADVICE
from core.session import ClinicalSession
from core.interceptors import MetricSanitizer
from core.exceptions import PhysiologicalBoundsViolation
from core.auth import rate_limit
from engines.model_engine import MLModelEngine
from engines.orchestrator import compile_comprehensive_diagnostics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── Security configuration ────────────────────────────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
    PERMANENT_SESSION_LIFETIME=3600,
)

active_cases: dict = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Security headers middleware ───────────────────────────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "img-src 'self' data:; "
        "frame-ancestors 'none';"
    )
    return response


# ── CSRF helpers ──────────────────────────────────────────────────────────────
def _get_or_create_csrf_token() -> str:
    if "csrf_token" not in flask_session:
        flask_session["csrf_token"] = secrets.token_hex(32)
    return flask_session["csrf_token"]


def _verify_csrf(data: dict) -> bool:
    token = data.get("_csrf") or request.headers.get("X-CSRF-Token", "")
    expected = flask_session.get("csrf_token", "")
    return secrets.compare_digest(token, expected) if (token and expected) else False

logger.info("MOUNTING MULTI-SPECIALTY CLINICAL DIAGNOSTIC PLATFORM")

ml_engines: dict = {}
for specialty_id, spec in SPECIALTY_FIELDS.items():
    engine_cfg = spec["engine"]
    if engine_cfg["type"] != "ml":
        continue
    model_path = os.path.join(BASE_DIR, engine_cfg["model_file"])
    engine = MLModelEngine(model_path, len(engine_cfg["feature_order"]), specialty_id)
    ml_engines[specialty_id] = engine
    status = "LOADED" if engine.is_available() else f"UNAVAILABLE ({engine.load_error})"
    logger.info("[%s] %s -> %s : %s", specialty_id, spec['title'], engine_cfg['model_file'], status)

logger.info("%d ML model(s), %d rule engine(s), %d total specialties registered.",
    len(ml_engines),
    len([s for s in SPECIALTY_FIELDS.values() if s['engine']['type'] == 'rule']),
    len(SPECIALTY_FIELDS))


# ── Template context helper ──────────────────────────────────────────────────
def _build_context():
    categories = {}
    for sid, spec in SPECIALTY_FIELDS.items():
        cat = spec.get("category", "Other")
        categories.setdefault(cat, []).append((sid, spec))
    return dict(
        tracks=SPECIALTY_FIELDS,
        categories=categories,
        global_fields=GLOBAL_BASELINE_FEATURES,
        advice=SPECIALTY_ADVICE,
        csrf_token=_get_or_create_csrf_token(),
    )


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', **_build_context())


@app.route('/classic-chat')
def classic_chat():
    ctx = _build_context()
    first_key = list(GLOBAL_BASELINE_FEATURES.keys())[0]
    ctx['first_prompt'] = GLOBAL_BASELINE_FEATURES[first_key]["prompt"]
    return render_template('index.html', **ctx)


# ── Dashboard API ─────────────────────────────────────────────────────────────
def _find_rules(key, track_id):
    if key in GLOBAL_BASELINE_FEATURES:
        return GLOBAL_BASELINE_FEATURES[key]
    if track_id in SPECIALTY_FIELDS and key in SPECIALTY_FIELDS[track_id]["registry"]:
        return SPECIALTY_FIELDS[track_id]["registry"][key]
    for spec in SPECIALTY_FIELDS.values():
        if key in spec["registry"]:
            return spec["registry"][key]
    return None


@app.route('/api/assess', methods=['POST'])
@rate_limit(max_calls=20, window_seconds=60)
def api_assess():
    data = request.get_json() or {}
    if not _verify_csrf(data):
        return jsonify({"error": "csrf_invalid", "message": "Invalid or missing CSRF token."}), 403
    track_id = data.get('trackId', 'ALL')
    raw_profile = data.get('profile', {})

    if track_id != 'ALL' and track_id not in SPECIALTY_FIELDS:
        return jsonify({'error': f"Unknown specialty '{track_id}'."}), 400

    sanitized_profile = {}
    field_errors = {}

    for key, value in raw_profile.items():
        if value is None or str(value).strip() == "":
            continue
        rules = _find_rules(key, track_id)
        if rules is None:
            continue
        try:
            sanitized_profile[key] = MetricSanitizer.process_and_validate(key, value, rules)
        except PhysiologicalBoundsViolation as e:
            field_errors[key] = str(e)
        except ValueError as e:
            field_errors[key] = str(e)

    if field_errors:
        return jsonify({'error': 'validation_failed', 'field_errors': field_errors}), 400

    results = compile_comprehensive_diagnostics(sanitized_profile, ml_engines)

    if track_id == 'ALL':
        return jsonify({'results': results, 'profile_used': sanitized_profile})
    return jsonify({'results': {track_id: results.get(track_id, {})}, 'profile_used': sanitized_profile})


# ── Classic chat API ──────────────────────────────────────────────────────────
@app.route('/chat', methods=['POST'])
@rate_limit(max_calls=30, window_seconds=60)
def chat():
    data = request.get_json() or {}
    if not _verify_csrf(data):
        return jsonify({"reply": "❌ Invalid CSRF token. Please refresh the page."}), 403
    user_id  = data.get('userId')
    track_id = data.get('trackId')
    user_msg = str(data.get('message', '')).strip()

    if not user_id or track_id not in SPECIALTY_FIELDS:
        return jsonify({'reply': "❌ Invalid session or unrecognized specialty tab."}), 400

    if user_id not in active_cases:
        active_cases[user_id] = ClinicalSession(user_id)

    session = active_cases[user_id]
    scope, current_key = session.determine_next_node(track_id)

    if current_key and user_msg:
        rules = (GLOBAL_BASELINE_FEATURES[current_key] if scope == "global"
                 else SPECIALTY_FIELDS[track_id]["registry"][current_key])
        try:
            session.patient_profile[current_key] = MetricSanitizer.process_and_validate(current_key, user_msg, rules)
        except PhysiologicalBoundsViolation as e:
            return jsonify({'reply': f"❌ <strong>Out of Range:</strong> {e} <br><br>💡 Please provide a clinically plausible value."})
        except ValueError as e:
            return jsonify({'reply': f"⚠️ <strong>Invalid Input:</strong> {e}"})
        except Exception as e:
            return jsonify({'reply': f"⚠️ <strong>Input Rejected:</strong> {e}"})

        if scope == "global":
            session.global_step += 1
        else:
            session.fields_state[track_id]["step"] += 1

    next_scope, next_key = session.determine_next_node(track_id)
    feedback_bubble = ""

    if scope == "global" and session.global_step > 0:
        prev_key   = session.global_queue[session.global_step - 1]
        prev_rules = GLOBAL_BASELINE_FEATURES[prev_key]
        if "max_optimal" in prev_rules and isinstance(session.patient_profile.get(prev_key), (int, float)) \
                and session.patient_profile[prev_key] > prev_rules["max_optimal"]:
            tip = f' <br>💡 <em>{prev_rules["tip"]}</em>' if "tip" in prev_rules else ""
            feedback_bubble = f"<div style='color:#f59e0b;border:1px solid #f59e0b;padding:10px;border-radius:6px;margin-bottom:10px;font-size:.88rem;'>⚠️ <strong>Elevated ({prev_key}):</strong> Above optimal range.{tip}</div>"
    elif scope == "specialty" and session.fields_state[track_id]["step"] > 0:
        local_state = session.fields_state[track_id]
        prev_key    = local_state["queue"][local_state["step"] - 1]
        prev_rules  = SPECIALTY_FIELDS[track_id]["registry"].get(prev_key, {})
        if "max_optimal" in prev_rules and isinstance(session.patient_profile.get(prev_key), (int, float)) \
                and session.patient_profile[prev_key] > prev_rules["max_optimal"]:
            tip = f' <br>💡 <em>{prev_rules["tip"]}</em>' if "tip" in prev_rules else ""
            feedback_bubble = f"<div style='color:#f59e0b;border:1px solid #f59e0b;padding:10px;border-radius:6px;margin-bottom:10px;font-size:.88rem;'>⚠️ <strong>Elevated ({prev_key}):</strong> Above optimal range.{tip}</div>"

    if next_key:
        rules = (GLOBAL_BASELINE_FEATURES[next_key] if next_scope == "global"
                 else SPECIALTY_FIELDS[track_id]["registry"][next_key])
        badge = ("<span style='color:#22d3ee;background:rgba(34,211,238,.1);padding:2px 6px;border-radius:4px;font-size:.75rem;font-weight:bold;margin-right:5px;'>SHARED BASELINE</span>"
                 if next_scope == "global" else
                 "<span style='color:#a78bfa;background:rgba(167,139,250,.1);padding:2px 6px;border-radius:4px;font-size:.75rem;font-weight:bold;margin-right:5px;'>SPECIALTY FIELD</span>")
        return jsonify({'reply': f"{feedback_bubble}{badge} <strong>{rules['prompt']}</strong>"})

    else:
        all_results = compile_comprehensive_diagnostics(session.patient_profile, ml_engines)
        title  = SPECIALTY_FIELDS[track_id]["title"]
        result = all_results.get(track_id, {})
        verdict   = result.get("verdict", "Insufficient inputs.")
        conf      = result.get("confidence", 0.0)
        status    = result.get("status", "UNKNOWN")
        eng_type  = result.get("engine_type", "unknown")
        top_drivers = result.get("top_drivers", [])

        advice_list = SPECIALTY_ADVICE.get(track_id, {}).get(status, [])

        color = "#22d3ee" if status == "NORMAL" else ("#f59e0b" if status == "ELEVATED_RISK" else "#ef4444")
        if status == "INDETERMINATE":
            color = "#fbbf24"

        eng_badge = (
            "<span style='font-size:.7rem;font-weight:bold;background:#22d3ee;color:#001f25;padding:2px 8px;border-radius:4px;margin-left:8px;'>🤖 ML MODEL</span>"
            if eng_type == "ml" else
            "<span style='font-size:.7rem;font-weight:bold;background:#a78bfa;color:#fff;padding:2px 8px;border-radius:4px;margin-left:8px;'>📋 SCORING ENGINE</span>"
        )
        conf_label = "Model Prediction Confidence" if eng_type == "ml" else "Clinical Criteria Score"

        drivers_html = ""
        if top_drivers:
            chips = " ".join(f"<span style='display:inline-block;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:2px 8px;font-size:.75rem;margin:2px 3px 0 0;'>{d['feature']} ({round(d['importance']*100)}%)</span>" for d in top_drivers)
            drivers_html = f"<p style='margin:10px 0 4px;font-size:.8rem;color:#94a3b8;'>Key drivers: {chips}</p>"

        advice_html = ""
        if advice_list:
            items = "".join(f"<li style='margin:5px 0;font-size:.85rem;'>{a}</li>" for a in advice_list)
            advice_html = f"<div style='margin-top:14px;padding:12px;background:rgba(34,211,238,.04);border:1px solid rgba(34,211,238,.2);border-radius:8px;'><div style='font-size:.75rem;font-weight:bold;text-transform:uppercase;letter-spacing:.05em;color:#22d3ee;margin-bottom:8px;'>💡 Clinical Guidance</div><ul style='margin:0;padding-left:18px;color:#cbd5e1;'>{items}</ul></div>"

        markup = f"""
        {feedback_bubble}
        <div style='border:1px solid {color};padding:20px;border-radius:10px;background:rgba(0,0,0,.2);'>
          <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;'>
            <h4 style='margin:0;color:{color};font-size:1.05rem;'>📋 {title}{eng_badge}</h4>
            <span style='font-size:.7rem;font-weight:bold;background:{color};color:#000;padding:2px 8px;border-radius:4px;'>STATUS: {status}</span>
          </div>
          <hr style='border:0;border-top:1px solid #1e293b;margin:12px 0;'/>
          <p style='margin:8px 0;'><strong>Verdict:</strong><br>
            <span style='color:#fff;font-family:monospace;display:block;margin-top:5px;background:#0c1324;padding:10px;border-radius:6px;border-left:3px solid {color};'>{verdict}</span>
          </p>
          <p style='margin:12px 0 4px;font-size:.85rem;color:#94a3b8;'><strong>{conf_label}:</strong> {conf:.1f}%</p>
          <div style='background:#1e293b;height:5px;border-radius:3px;overflow:hidden;margin-bottom:10px;'>
            <div style='background:{color};width:{conf}%;height:100%;transition:width .5s;'></div>
          </div>
          {drivers_html}
          {advice_html}
          <hr style='border:0;border-top:1px solid #1e293b;margin:14px 0 10px;'/>
          <button style='background:#111827;border:1px solid #334155;color:#94a3b8;padding:7px 12px;border-radius:6px;cursor:pointer;font-size:.8rem;font-weight:600;' onclick="toggleGlobalDataDump(this)">Inspect Shared Patient Profile</button>
          <div class="data-dump" style="display:none;margin-top:10px;background:#000;padding:12px;border-radius:6px;font-family:monospace;font-size:.82rem;color:#34d399;max-height:140px;overflow-y:auto;border:1px solid #1e293b;">
            <strong>Shared patient profile (reused across all tabs):</strong><br><br>{str(session.patient_profile)}
          </div>
        </div>
        """
        return jsonify({'reply': markup})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    app.run(host='127.0.0.1', port=port, debug=debug)
