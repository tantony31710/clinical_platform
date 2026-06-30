# Multi-Specialty Clinical Diagnostic Console

A Flask platform covering **17 medical specialty modules**, presented as a
**form-based clinical dashboard** (not a chatbot). Where a real, clean
public dataset was available, a module runs a **real, probability-calibrated,
trained scikit-learn model** with feature-importance reporting. Everywhere
else, it runs a **real, named, validated clinical scoring tool**. Both are
clearly labeled in the UI.

⚠️ **Educational / demonstration project.** Not an FDA-cleared or CE-marked
medical device, not validated for clinical use, not a substitute for a
qualified clinician. **See [`ROADMAP.md`](ROADMAP.md)** for the honest,
detailed answer to "how do I make this a real medical device" — TL;DR: it's
a multi-year regulatory and clinical-validation process that runs through
clinicians and regulators, not through more code.

## Interfaces

The application is served from the root URL (`/`) and presents a unified
**clinical dashboard**. This interface provides structured intake forms per
specialty, a shared "Patient Baseline" panel for common metrics, and supports
both single-specialty and full 17-module panel assessments. Results are
delivered with calibrated confidence scores, uncertainty banding for ML models,
and feature-importance explanations.

## What's real and how it was sourced

This sandbox has no general internet access (outbound network is blocked at
the egress proxy, and GitHub raw files specifically reject automated fetches
via robots.txt). So instead of faking 17 datasets, the build uses exactly
what could be obtained reliably:

| # | Specialty | Engine | Source |
|---|---|---|---|
| 1 | Diabetes (Metabolic) | **Real ML**, calibrated | Pima Indians Diabetes Database, NIDDK — 768 patients (your upload) |
| 2 | Heart Disease (Cardiology) | **Real ML**, calibrated | Cleveland-style heart dataset — 1190 patients (your upload) |
| 3 | Chronic Kidney Disease (Nephrology) | **Real ML**, calibrated | UCI Chronic Kidney Disease dataset — 158 patients |
| 4 | Breast Cancer (Oncology) | **Real ML**, calibrated | Breast Cancer Wisconsin (Diagnostic), scikit-learn built-in — 569 patients |
| 5–17 | Cervical oncology, Hepatology, Pulmonology, Stroke/Neurology, Sepsis/Infectious Disease, Rheumatology, Psychiatry, Thyroid/Endocrinology, Hematology, Dermatology, Urology, Ophthalmology, Orthopedics | **Real validated clinical scoring tools** | qSOFA (Sepsis-3), PHQ-9, CHA₂DS₂-VASc, KDIGO-style staging, GOLD criteria, ABCDE melanoma criteria, APRI liver score, WHO anemia criteria, standard lab reference ranges, FRAX-like fracture risk factors |

### Model rigor

The 4 ML models go through **sigmoid probability calibration**
(`CalibratedClassifierCV`, 5-fold) during training, so the confidence values
the app reports track real-world observed frequency rather than raw
uncalibrated model votes. Honest metrics — held-out accuracy (raw and
calibrated), 5-fold CV accuracy, AUC, and Brier score — are written to
`models/training_report.json` on every training run:

- Diabetes: ~75% CV accuracy, AUC 0.82
- Heart Disease: ~89% CV accuracy, AUC 0.95
- Chronic Kidney Disease: ~97–99% CV accuracy, AUC ~1.0 (small, fairly separable dataset)
- Breast Cancer: ~93% CV accuracy, AUC 0.98

Predictions whose calibrated probability falls between 40–60% are reported
as **INDETERMINATE** rather than forced into a high/low verdict — a
genuinely uncertain model output should say so, not pick a side. Each ML
result also reports its top 3 most influential features (population-level
importance from the trained model, explicitly labeled as such — this is
*not* a per-patient explanation, since that would need SHAP/treeinterpreter
analysis this build doesn't include).

If you have access to better/larger datasets for any of the rule-based
specialties, drop the CSV into `data/`, add a training block to
`models/train_models.py`, flip that specialty's `engine.type` to `"ml"` in
`config/specialties.py`, and it'll be picked up automatically — nothing
else in the codebase needs to change (see "Architecture" below).

## Architecture

This is a full rewrite from the original single-disease monolith into a
config-driven, zero-branching design:

```
clinical_platform/
├── app.py                     # Flask routes — fully generic, no per-disease code
├── ROADMAP.md                 # Honest path to real medical-device status
├── config/
│   └── specialties.py         # The ONE file that defines every module: prompts,
│                               # validation ranges, and which engine runs it
├── core/
│   ├── interceptors.py        # Input validation/sanitization
│   └── exceptions.py
├── engines/
│   ├── model_engine.py        # Generic loader/runner for ANY calibrated sklearn model
│   ├── rule_engines.py        # The 13 real clinical scoring functions
│   └── orchestrator.py        # Loops every specialty, dispatches ML vs rule
├── models/
│   ├── train_models.py        # Re-run any time a dataset changes; calibrates + reports metrics
│   ├── *.pkl                  # 4 trained, calibrated model files
│   └── training_report.json   # Honest accuracy/AUC/Brier/feature-importance numbers
├── data/                      # Source CSVs for the 4 ML models
├── templates/                 # Jinja2 templates for the Flask UI
│   ├── dashboard.html         # The main dashboard interface
│   ├── history.html           # Patient assessment history view
│   └── performance.html       # ML model performance report view
└── requirements.txt
```

**Adding specialty #18** means adding one dict entry to
`config/specialties.py` (prompts + validation rules + which engine). Nothing
in `app.py`, `session.py`, or `orchestrator.py` is aware of how many
specialties exist or what they're called — the original code had hardcoded,
copy-pasted per-disease functions for every new disease; this version
doesn't.

## Smart cross-tab reuse

Patient measurements are shared across the whole session. A few examples
already wired up: `Hemoglobin` entered in Nephrology auto-fills Hematology;
`HypertensionHistory` / `DiabetesMellitusHistory` entered in Nephrology
auto-fill Neurology's stroke-risk score; `BMI` entered in Metabolic is
opportunistically reused by Orthopedics' fracture-risk scoring. Age, Sex,
systolic blood pressure, and smoking status are asked once globally and
used everywhere.

## Running it

```bash
pip install -r requirements.txt
python3 models/train_models.py   # regenerates the 4 .pkl files from data/
python3 app.py                   # serves on http://127.0.0.1:5000
```

## Safety notes

- The Psychiatry tab implements the real PHQ-9 screening instrument. If the
  self-harm item (item 9) is endorsed at all, the verdict flags it for
  urgent follow-up regardless of the total score, and surfaces a prompt to
  contact emergency services or a crisis line if there's immediate danger.
- All verdicts are demonstration output, not diagnoses. The header banner
  and this README both say so on purpose — please keep that disclaimer if
  you deploy this anywhere beyond a personal demo.
