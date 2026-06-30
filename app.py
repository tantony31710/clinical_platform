# app.py
from flask import Flask, request, jsonify, render_template, Response
import io
import csv
import os
import json

from config.specialties import GLOBAL_BASELINE_FEATURES, SPECIALTY_FIELDS
from core.interceptors import MetricSanitizer
from core.exceptions import PhysiologicalBoundsViolation
from engines.model_engine import MLModelEngine 
from core.db import init_db, save_assessment, get_patient_history, DatabaseConnection
from engines.orchestrator import compile_comprehensive_diagnostics

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print(" MOUNTING MULTI-SPECIALTY CLINICAL DIAGNOSTIC PLATFORM")
init_db()
print("=======================================================")

# Lazily build one MLModelEngine per "ml"-type specialty. Adding a new ML
# specialty to config/specialties.py is picked up automatically here --
# nothing in this loop is disease-specific.
ml_engines = {}
for specialty_id, spec in SPECIALTY_FIELDS.items():
    engine_cfg = spec["engine"]
    if engine_cfg["type"] != "ml":
        continue
    model_path = os.path.join(BASE_DIR, engine_cfg["model_file"])
    expected_dim = len(engine_cfg["feature_order"])
    engine = MLModelEngine(model_path, expected_dim, specialty_id)
    ml_engines[specialty_id] = engine
    status = "✅ LOADED" if engine.is_available() else f"⚠️  UNAVAILABLE ({engine.load_error})"
    print(f"  [{specialty_id}] {spec['title']} -> {engine_cfg['model_file']} : {status}")

print(f"\n  {len(ml_engines)} ML model(s) registered, "
      f"{len([s for s in SPECIALTY_FIELDS.values() if s['engine']['type'] == 'rule'])} rule engine(s) registered, "
      f"{len(SPECIALTY_FIELDS)} total specialty tabs.\n")


@app.route('/dashboard')
def dashboard():
    categories = {}
    for specialty_id, spec in SPECIALTY_FIELDS.items():
        cat = spec.get("category", "Other")
        categories.setdefault(cat, []).append((specialty_id, spec))
    return render_template('dashboard.html', active_page='dashboard', tracks=SPECIALTY_FIELDS,
                           categories=categories, global_fields=GLOBAL_BASELINE_FEATURES)


def _find_field_rules(key, track_id):
    """A submitted field key might be global, or belong to the active specialty,
    or be a reused key from a different specialty (cross-tab reuse, e.g. Hemoglobin).
    Search in that priority order."""
    if key in GLOBAL_BASELINE_FEATURES:
        return GLOBAL_BASELINE_FEATURES[key]
    if track_id in SPECIALTY_FIELDS and key in SPECIALTY_FIELDS[track_id]["registry"]:
        return SPECIALTY_FIELDS[track_id]["registry"][key]
    for spec in SPECIALTY_FIELDS.values():
        if key in spec["registry"]:
            return spec["registry"][key]
    return None


@app.route('/api/assess', methods=['POST'])
def api_assess():
    """
    Form-based assessment endpoint for the dashboard UI. Accepts the full
    set of values the clinician has entered (profile), validates each
    non-empty one, and runs either a single specialty's engine or the full
    17-specialty panel.
    """
    data = request.get_json() or {}
    track_id = data.get('trackId', 'ALL')
    raw_profile = data.get('profile', {})

    if track_id != 'ALL' and track_id not in SPECIALTY_FIELDS:
        return jsonify({'error': f"Unknown specialty '{track_id}'."}), 400

    sanitized_profile = {}
    field_errors = {}

    for key, value in raw_profile.items():
        if value is None or str(value).strip() == "":
            continue
        rules = _find_field_rules(key, track_id)
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

    # If a specific track is requested, run only that one. Otherwise, run all.
    specialty_to_run = track_id if track_id != 'ALL' else None
    diagnostics_manifest = compile_comprehensive_diagnostics(sanitized_profile, ml_engines, specialty_to_run)

    # For a full-panel run, persist the results to the patient's history
    # We'll use a hardcoded patient_id for this demonstration.
    if track_id == 'ALL':
        patient_id = "patient_001" # In a real app, this would come from a session/login
        save_assessment(patient_id, sanitized_profile, diagnostics_manifest)

    if track_id == 'ALL':
        return jsonify({'results': diagnostics_manifest, 'profile_used': sanitized_profile})
    else:
        return jsonify({'results': diagnostics_manifest, 'profile_used': sanitized_profile})


@app.route('/api/history', methods=['GET'])
def api_history():
    """
    New endpoint to fetch historical assessment data for trend analysis.
    """
    patient_id = request.args.get('patientId', "patient_001") # Demo default
    history = get_patient_history(patient_id)
    return jsonify(history)

@app.route('/history')
def history_page():
    """
    New page to display a patient's full assessment history from the database.
    """
    patient_id = request.args.get('patientId', "patient_001") # Demo default
    history_data = get_patient_history(patient_id)
    # The history is ordered oldest to newest. For display, newest first is better.
    history_data.reverse()
    return render_template('history.html', active_page='history', history=history_data, patient_id=patient_id)

@app.route('/performance')
def performance():
    """
    New page to display the model training and performance report.
    """
    report_path = os.path.join(BASE_DIR, 'models', 'training_report.json')
    try:
        with open(report_path, 'r') as f:
            performance_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not load performance report: {e}")
        performance_data = {}

    # Separate environment from models for cleaner presentation
    environment = performance_data.pop('_environment', {})
    # The rest are the model reports
    models = performance_data

    return render_template('performance.html', active_page='performance', models=models, environment=environment)

@app.route('/api/health')
def api_health():
    """A simple endpoint to check if the server is up and the database is connected."""
    db_status = "disconnected"
    db_error = "No error"
    try:
        # This will use the DatabaseConnection context manager to test a connection
        with DatabaseConnection() as conn:
            with conn.cursor() as cursor:
                # Execute a simple, fast query
                cursor.execute("SELECT 1")
                cursor.fetchone()
        db_status = "connected"
        return jsonify({"server_status": "ok", "database_status": db_status})
    except Exception as e:
        db_error = str(e)
        return jsonify({"server_status": "ok", "database_status": db_status, "error": db_error, "troubleshooting": "Check Vercel environment variables for DATABASE_URL and Supabase network restrictions (firewall)."}), 500

@app.route('/api/export/csv', methods=['GET'])
def api_export_csv():
    """
    New endpoint to export a patient's full assessment history as a CSV file.
    This is ideal for data scientists and researchers.
    """
    patient_id = request.args.get('patientId', "patient_001") # Demo default
    history = get_patient_history(patient_id)

    if not history:
        return "No history found for this patient.", 404

    # Dynamically generate headers from all keys present in the historical data
    profile_keys = set()
    result_keys = set()
    for assessment in history:
        profile_keys.update(assessment['profile'].keys())
        for specialty, res in assessment['results'].items():
            for key in res.keys():
                result_keys.add(f"{specialty}_{key}")

    # Sort for consistent column order
    fieldnames = ['timestamp', 'patient_id'] + sorted(list(profile_keys)) + sorted(list(result_keys))

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for assessment in history:
        row = {'patient_id': patient_id, 'timestamp': assessment['timestamp']}
        # Add profile data
        row.update(assessment['profile'])
        # Flatten and add results data
        for specialty, res in assessment['results'].items():
            for key, value in res.items():
                row[f"{specialty}_{key}"] = value
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=patient_{patient_id}_history.csv"}
    )

@app.route('/')
def index():
    return dashboard()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
